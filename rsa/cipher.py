import random
from time import time
from typing import Union, Tuple, Literal
from sieve import first_100_primes_list
from math import gcd
from fast_pow_mod import fast_pow_mod
from euclid_extended import find_inverse
from functools import wraps


def discard_padding(decipher_func):
    @wraps(decipher_func)
    def inner(*args, **kwargs):
        res = decipher_func(*args, **kwargs)
        result = bytes(0)
        for i in range(0, len(res), 256):
            chunk = res[i:i+256]
            j = 0
            for byte in chunk:
                if byte == 127:
                    break
                j += 1
            result += chunk[j + 1:]

        for i in range(1, 257):
            if result[-i] == 128:
                return result[:-i]
        return None
    return inner


class RSA:
    def __init__(self,
                 cipher_key: Literal["public", "private"] = "public",
                 # key_len_bits : Literal[2048, 4096] = 2048,
                 key: Union[None, Tuple[Tuple[int, int], Tuple[int, int]]] = None) -> None:
        """
        :param cipher_key: indicate which keys - public or private, it will use to cipher
        :param key: a pair of private and public keys ((d, n), (e, n)), by default they will be generated
        """
        # self.key_len_bits = (len(bin(key[0][0])) - 2) if key else 2048
        self.key_len_bits = 2048
        # assert self.key_len_bits in (2048, 4096)
        self.private_key, self.public_key = key or self.generate_keys()
        self.cipher_key = cipher_key

        check = 0x6f77202c6f6c6c654821646c726f77202c6f6c6c6548216246c726f77202c6f6c6c654821646c726f77202c6f6c6c654821646
        assert check == fast_pow_mod(fast_pow_mod(check, self.private_key[0], self.private_key[1]),  # check keys
                                     self.public_key[0],
                                     self.public_key[1])
        assert check == fast_pow_mod(fast_pow_mod(check, self.public_key[0], self.public_key[1]),  # check keys
                                     self.private_key[0],
                                     self.private_key[1])

    def generate_keys(self) -> Union[None, Tuple[Tuple[int, int], Tuple[int, int]]]:
        while True:
            while True:
                p = self.get_low_level_prime()
                if self.is_Miller_Rabin_test_passed(p):
                    break
            # print(f"p = {p}")
            while True:
                q = self.get_low_level_prime()
                if q != p and self.is_Miller_Rabin_test_passed(q):
                    break
            if len(bin(n := p * q)) - 2 >= 2048:
                break
        # print(f"q = {q}")

        # print(f"n = {n}")
        phi = (p - 1) * (q - 1)
        # print(f"phi = {phi}")
        while True:
            e = random.randrange(2, phi)
            if gcd(phi, e) == 1:
                break
        # print(f"e = {e}")
        # e_inverse = fast_pow_mod(e, phi - 1, n)
        e_inverse = find_inverse(e, phi)
        # print(f"e_inverse = {e_inverse}")
        assert (e * e_inverse) % phi == 1
        # print((e * e_inverse) % n)
        d = e_inverse % phi
        # print((d * e) % phi)
        return (d, n), (e, n)

    def n_bit_random(self):
        """
        Returns a random number
        between 2**(n-1)+1 and 2**n-1
        """
        n = self.key_len_bits // 2
        return random.randrange(2 ** (n - 1) + 1, 2 ** n - 1)

    def get_low_level_prime(self):
        first_primes_list = first_100_primes_list
        while True:
            prime_candidate = self.n_bit_random()

            for divisor in first_primes_list:
                if (prime_candidate % divisor == 0) and (divisor ** 2 <= prime_candidate):
                    break
            # If no divisor found, return value
            else:
                return prime_candidate

    @staticmethod
    def is_Miller_Rabin_test_passed(miller_rabin_candidate):
        max_divisions_by_2 = 0
        even_component = miller_rabin_candidate - 1

        while even_component % 2 == 0:
            even_component >>= 1
            max_divisions_by_2 += 1
        assert (2 ** max_divisions_by_2 * even_component == miller_rabin_candidate - 1)

        def trial_composite(round_tester_):
            if pow(round_tester_, even_component, miller_rabin_candidate) == 1:
                return False
            for i in range(max_divisions_by_2):
                if pow(round_tester_, 2 ** i * even_component, miller_rabin_candidate) == miller_rabin_candidate - 1:
                    return False
            return True

        # Set number of trials here
        number_of_Rabin_trials = 20
        for i in range(number_of_Rabin_trials):
            round_tester = random.randrange(2, miller_rabin_candidate)
            if trial_composite(round_tester):
                return False
        return True

    def cipher_block(self, text: bytes):
        text = int.from_bytes(text, 'big')
        return fast_pow_mod(text, self.private_key[0], self.private_key[1]).to_bytes(256, 'big') if self.cipher_key == "private" \
            else fast_pow_mod(text, self.public_key[0], self.public_key[1]).to_bytes(256, 'big')  # self.cipher_key == "public"

    def decipher_block(self, cipher_text: bytes):
        cipher_text = int.from_bytes(cipher_text, 'big')
        # cipher_text = 578791089776172078287924841073265544359778882254729774830393510436118414474740162532866697556410180917590295888033545046379324873376627348917577435525867557719290162773223152868885033273009908897361650688683242581104928881380231910159524513545643509322677433540941409178313709999183344383239549163532071184499609863163857395148837239412961358120678181909019447288926664689083711436859520792426856261083358768976380045100393916972622069354037205351475310350091370898269001332673031118363843111082350055514543965654834876474380361411019026328852815920860731944205284367332297864960143720470249130335746041418069019195
        return fast_pow_mod(cipher_text, self.private_key[0], self.private_key[1]).to_bytes(256, 'big') if self.cipher_key == "public" \
            else fast_pow_mod(cipher_text, self.public_key[0], self.public_key[1]).to_bytes(256, 'big')  # self.cipher_key == "private"

    def cipher(self, big_text_bytes: bytes):
        # print("openedtext:", (len(big_text) - 2) / 2, hex(big_text))
        block_size_bytes = self.key_len_bits // 8 - 1

        cur_len = len(big_text_bytes)
        if cur_len % block_size_bytes:
            big_text_bytes += b'\x80'
            big_text_bytes += bytes(block_size_bytes - (cur_len % block_size_bytes + 1))
        else:
            big_text_bytes += b'\x80'
            big_text_bytes += bytes(block_size_bytes - 1)
        cur_len = len(big_text_bytes)
        res = bytes(0)
        start = 0

        while cur_len:
            block = big_text_bytes[start:block_size_bytes + start]
            block = (127).to_bytes(1, 'big') + block
            start += block_size_bytes
            ciphered = self.cipher_block(block)
            res += ciphered
            # print("cbres", ciphered)
            cur_len -= block_size_bytes
        return res

    @discard_padding
    def decipher(self, big_cipher_text_bytes: bytes):
        block_size_bytes = self.key_len_bits // 8
        cur_len = len(big_cipher_text_bytes)

        res = bytes(0)
        start = 0
        while cur_len:
            block = big_cipher_text_bytes[start:block_size_bytes + start]
            # print("dlock", block)
            start += block_size_bytes
            deciphered = self.decipher_block(block)
            res += deciphered
            # print("dbres", deciphered)
            cur_len -= block_size_bytes

        return res


if __name__ == "__main__":
    t = time()
    Alice = RSA(cipher_key="public",
                key=((7480141088041407660932715068102356829405362283693079080905061825338971880424779842367106737590135773928960812539803705125152923491152839865534274103230080429241200247824770787678359305293461660930373936072223448957787144201154689332159948151329963066056425646946981381454945093474647358412534495719065889825598576421448874992686973138272649668578352004574566103892285754981186780973899490451982425995293312677986395493723624086408491589339013983649711287294455879343184817862227304189022999236799563214276869282420979808053127535055628270740648949381545606991648462994785703407841318870613708449916151798599595306957, 23118370650264136922803070123686081957677143840821696523460217460870645634569147413599154016034643332363608658046080506879547467705471466851471946488560348217805565478197034680904107137806734241826873759783998058918881473083994648114937615018842073244136362664915646041885535979824256117099718379703468554021104475041936588125773984095095680448355144794283733317389049110796116365366393698539007809524017172564469543557298886127714719198140143163133172633982286507650706324237548228073018772746566550459222013131887154720242369786528189663080924594408900488868611248757114370234139990661088895586460878196645998868989), (3722184951011495883172631262603631392924611348346860987637297560359813423533507032621512364934777371813733710239634102419486734702697883099962199509189297476774400228718415860380584161388801963511082569573197906650868391335231880420529915798748755029921213624557522844675818400232031339522296136157954837287492859581015077895953987246795238908195626073178600212279056227429294012677189151520385636432837429531416739262788915744706108144454068571101641635293037020519730371993662788119484785072651078891496924010811236997620056415544816759421479511424125785184360086018319981114076046084093043491675926374081074528689, 23118370650264136922803070123686081957677143840821696523460217460870645634569147413599154016034643332363608658046080506879547467705471466851471946488560348217805565478197034680904107137806734241826873759783998058918881473083994648114937615018842073244136362664915646041885535979824256117099718379703468554021104475041936588125773984095095680448355144794283733317389049110796116365366393698539007809524017172564469543557298886127714719198140143163133172633982286507650706324237548228073018772746566550459222013131887154720242369786528189663080924594408900488868611248757114370234139990661088895586460878196645998868989))
                )
    #print(((Alice.private_key[0], Alice.private_key[1]),  (Alice.public_key[0], Alice.public_key[1])))
    print(f"keygen time spent: {time() - t}")
    msg = ('Hello, world!' * int(100)).encode('ascii')
    # msg = ('Z' * 2561).encode('ascii')
    # msg = b'\xff' * 2551
    print(f"message   text: {msg}")
    t = time()
    c = Alice.cipher(msg)
    print(f"encrypted text: {c}")
    deciphered_text = Alice.decipher(c)
    print(f"decrypted text: {deciphered_text}")
    assert msg == deciphered_text
    print(f"time spent: {time() - t}")
