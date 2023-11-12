import math
import os


class RC6:
    def __init__(self, w=32, r=20, key_len=16):
        self.w = w  # word len (4 words - 1 block)
        self.r = r  # number of rounds
        self.b = key_len  # secret key len
        self.module = 2 ** self.w

    def cycle_permutation(self, number, number_of_shift):
        """L - number, k - number of shift (positive - left, negative - right)"""
        if abs(number_of_shift) > self.w:
            number_of_shift %= self.w

        if number_of_shift > 0:
            number_to_shift = number // (2 ** (self.w - number_of_shift))
            result = number % (2 ** (self.w - number_of_shift))
            result = result << number_of_shift
            result += number_to_shift
            return result
        else:
            number_of_shift_abs = abs(number_of_shift)
            number_to_shift = number % (2 ** number_of_shift_abs)
            result = number >> number_of_shift_abs
            result += number_to_shift << (self.w - number_of_shift_abs)
            return result

    def key_schedule(self, private_key):
        p_w = math.floor((math.e - 2) * (2 ** self.w))  # const e
        q_w = math.floor((math.sqrt(1.25) - 0.5) * (2 ** self.w))  # const golden ratio
        if p_w % 2 == 0:  # rounding to the closest odd number
            p_w += 1
        if q_w % 2 == 0:  # rounding to the closest odd number
            q_w += 1
        u = self.w // 8
        if self.b == 0:
            c = 1
        else:
            c = int(self.b / u)
        L = [0 for _ in range(c)]
        for i in range(self.b - 1, -1, -1):
            L[i // u] = sum([self.cycle_permutation(L[i // u], 8), private_key[i]]) % self.module
        # print('L:',' '.join(bin(i) for i in L),L[0].bit_length())
        # print('key:',' '.join(bin(i) for i in key))
        S = [p_w]
        for i in range(1, 2 * self.r + 4):
            S.append(sum([S[i - 1], q_w]) % self.module)
        A = B = i = j = 0
        v = 3 * max(c, 2 * self.r + 4)
        # permutation
        for k in range(v):
            A = S[i] = self.cycle_permutation(sum([S[i], A, B]) % self.module, 3)
            B = L[j] = self.cycle_permutation(sum([L[j], A, B]) % self.module, sum([A, B]) % self.module)
            i = int((i + 1) % (2 * self.r + 4))
            j = int((j + 1) % c)
        return S

    def store_text(self, arr: list):
        result = 0
        shift = 8
        for i in arr:
            result = (result << shift) + i
        if (len(arr) < self.w // 8) and not(result == 0):
            result = (result << (self.w // 8 - len(arr)) * shift)
        return result

    def parse_text(self, block_part):
        result = []
        shift = 256
        for i in range(self.w // 8):
            result.insert(0, block_part % shift)
            block_part = block_part // shift
        return result

    def encrypt(self, plaintext, private_key):
        S = self.key_schedule(private_key)
        ciphertext = bytearray()
        block_part_size = self.w // 8
        for j in range(0, len(plaintext), block_part_size*4):
            A = self.store_text(plaintext[j: j + block_part_size])
            B = self.store_text(plaintext[j + block_part_size: j + 2 * block_part_size])
            C = self.store_text(plaintext[j + 2 * block_part_size: j + 3 * block_part_size])
            D = self.store_text(plaintext[j + 3 * block_part_size: j + 4 * block_part_size])
            B = sum([S[0], B]) % self.module
            D = sum([S[1], D]) % self.module
            for i in range(1, self.r + 1):
                t = self.cycle_permutation((B * (2 * B + 1)) % self.module, int(math.log2(self.w)))
                u = self.cycle_permutation((D * (2 * D + 1)) % self.module, int(math.log2(self.w)))
                A = sum([self.cycle_permutation(A ^ t, u), S[2 * i]]) % self.module
                C = sum([self.cycle_permutation(C ^ u, t), S[2 * i + 1]]) % self.module
                A, B, C, D = B, C, D, A
            A = sum([A, S[2 * self.r + 2]]) % self.module
            C = sum([C, S[2 * self.r + 3]]) % self.module
            for k in [A, B, C, D]:
                text_arr = self.parse_text(k)
                for i in text_arr:
                    ciphertext.append(i)
        return ciphertext

    def decrypt(self, ciphertext, private_key):
        S = self.key_schedule(private_key)
        decrypted_arr = bytearray()
        block_part_size = self.w // 8
        for j in range(0, len(ciphertext), 4 * block_part_size):
            A = self.store_text(ciphertext[j: j + block_part_size])
            B = self.store_text(ciphertext[j + block_part_size: j + 2 * block_part_size])
            C = self.store_text(ciphertext[j + 2 * block_part_size: j + 3 * block_part_size])
            D = self.store_text(ciphertext[j + 3 * block_part_size: j + 4 * block_part_size])
            C = (C - S[2 * self.r + 3] + self.module) % self.module
            A = (A - S[2 * self.r + 2] + self.module) % self.module
            for i in range(self.r, 0, -1):
                A, B, C, D = D, A, B, C
                u = self.cycle_permutation((D * (2 * D + 1)) % self.module, int(math.log2(self.w)))
                t = self.cycle_permutation((B * (2 * B + 1)) % self.module, int(math.log2(self.w)))
                C = self.cycle_permutation((C - S[2 * i + 1] + self.module) % self.module, -t) ^ u
                A = self.cycle_permutation((A - S[2 * i] + self.module) % self.module, -u) ^ t
            D = (D - S[1] + self.module) % self.module
            B = (B - S[0] + self.module) % self.module
            for k in [A, B, C, D]:
                text_arr = self.parse_text(k)
                for i in text_arr:
                    decrypted_arr.append(i)
        return decrypted_arr


if __name__ == "__main__":
    mode = 0
    while not(mode == 3):
        print(f"Choose action:\n\t1.Encrypt\n\t2.Decrypt\n\t3.Change paths\n\t4.Exit")
        mode = int(input())
        s_encrypt = RC6()
        input_file_path = 'input.txt'
        match mode:
            case 1:
                input_file = open(input_file_path, 'rb')
                text = input_file.read()
                input_file.close()
                print(f"Received text:\t\t{text}")
                # text = [0] * 16
                key = os.urandom(16)
                print(f"Key (hex):\t\t\t{key.hex().upper()}")
                key_file = open('key.txt', 'wb')
                key_file.write(key)
                key_file.close()
                cypher_text = s_encrypt.encrypt(text, key)
                print(f"Ciphertext (hex):\t{cypher_text.hex().upper()}")
                output_file = open('encrypted_text.txt', 'wb')
                output_file.write(cypher_text)
                output_file.close()
            case 2:
                key_file = open('key.txt', 'rb')
                key = key_file.read()
                key_file.close()
                print(f"Key (hex):\t\t{key.hex().upper()}")
                input_file = open('encrypted_text.txt', 'rb')
                cypher_text = input_file.read()
                input_file.close()
                print(f"Received text:\t{cypher_text.hex().upper()}")
                decrypted_text = s_encrypt.decrypt(cypher_text, key)
                print(f"Decrypt (hex):\t{decrypted_text.hex().upper()}")
                decrypted_str = ''.join(chr(i) for i in decrypted_text)
                print(f"\t\t\t\t{decrypted_str}")
                output_file = open('decrypted_text.txt', 'w')
                print(f"{decrypted_str}", file=output_file)
                output_file.close()
            case 3:
                print(f"Choose path:\n\t1.Encrypt path\n\t2.Decrypt path\n\t3.Change paths\n\t4.back")
                mode = int(input())
            case 4:
                print(f"Closing...")


