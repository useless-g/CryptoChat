import random
from math import gcd, sqrt, ceil
from time import time
from typing import Tuple

from rsa.fast_pow_mod import fast_pow_mod
from rsa.sieve import first_100_primes_list


def gen_g_p() -> Tuple[int, int]:
    while True:
        while True:
            p = get_low_level_prime()
            if is_Miller_Rabin_test_passed(p):
                break

        phi = (p - 1)
        print(p)  # modulo for DH

        # ищем первообразный корень
        for g in range(2, p):
            if gcd(g, p) != 1:
                continue
            print(g)

            for i in range(2, ceil(sqrt(phi))):
            # for i in range(1, phi // 2):
                if phi % i:
                    continue
                if fast_pow_mod(g, phi // i, p) == 1:  # bad, not root
                    break

            else:
                if fast_pow_mod(g, phi, p) == 1:  # good, g is root
                    break
        else:
            continue
        break
    return g, p


def n_bit_random(key_len_bits):
    """
    Returns a random number
    between 2**(n-1)+1 and 2**n-1
    """
    n = key_len_bits // 2
    return random.randrange(2 ** (n - 1) + 1, 2 ** n - 1)


def get_low_level_prime():
    first_primes_list = first_100_primes_list
    while True:
        prime_candidate = n_bit_random(103)

        for divisor in first_primes_list:
            if (prime_candidate % divisor == 0) and (divisor ** 2 <= prime_candidate):
                break
        # If no divisor found, return value
        else:
            return prime_candidate


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


t = time()
print(gen_g_p())
print(time() - t)
