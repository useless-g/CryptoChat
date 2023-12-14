class SHA:
    def __init__(self):
        # l_b_table = {0: 25, 1: 50, 2: 100, 3: 200, 4: 400, 5: 800, 6: 1600}
        # self.l = 6
        # self.b = l_b_table[self.l]
        self.k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
                  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
                  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
                  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
                  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
                  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
                  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
        self.w = 32
        self.module = 2 ** self.w

    @staticmethod
    def padding(m):
        length = len(m)
        number_of_zeros = 55 - length % 64 + 8 - ((length.bit_length()-1) // 8 + 1)
        m.append(0x80)
        m += bytearray(0 for _ in range(number_of_zeros))
        m.append((length * 8) % 256)
        pos = len(m) - 1
        length = length >> 5
        while length != 0:
            m.insert(pos, length % 256)
            length = length >> 8
        return m

    @staticmethod
    def word_parsing(word_parts: list):
        result = []
        for i in range(0, len(word_parts) - 3, 4):
            result.append((int(word_parts[i]) << 24) + (int(word_parts[i + 1]) << 16) + (int(word_parts[i + 2]) << 8) + (int(word_parts[i + 3])))
        return result

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

    @staticmethod
    def ch(x, y, z):
        return (x & y) ^ (~x & z)

    @staticmethod
    def maj(x, y, z):
        return (x & y) ^ (x & z) ^ (y & z)

    def Sigma_0(self, x):
        return self.cycle_permutation(x, -2) ^ self.cycle_permutation(x, -13) ^ self.cycle_permutation(x, -22)

    def Sigma_1(self, x):
        return self.cycle_permutation(x, -6) ^ self.cycle_permutation(x, -11) ^ self.cycle_permutation(x, -25)

    def sigma_0(self, x):
        return self.cycle_permutation(x, -7) ^ self.cycle_permutation(x, -18) ^ (x >> 3)

    def sigma_func_1(self, x):
        return self.cycle_permutation(x, -17) ^ self.cycle_permutation(x, -19) ^ (x >> 10)

    def hash(self, msg):
        msg = self.padding(msg)
        hash_values = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
        for i in range(0, len(msg)-63, 64):
            word = self.word_parsing(msg[i:i + 64])
            for t in range(16, 64):
                word.append((self.sigma_func_1(word[t - 2]) + word[t - 7] + self.sigma_0(word[t - 15]) + word[t - 16]) % self.module)
            # print(len(word))
            # print(list(format(x,'0>32b') for x in word[:16]))
            a = hash_values[0]
            b = hash_values[1]
            c = hash_values[2]
            d = hash_values[3]
            e = hash_values[4]
            f = hash_values[5]
            g = hash_values[6]
            h = hash_values[7]
            for t in range(64):
                t1 = (h + self.Sigma_1(e) + self.ch(e, f, g) + self.k[t] + word[t]) % self.module
                t2 = (self.Sigma_0(a) + self.maj(a, b, c)) % self.module
                h, g, f, e, d, c, b, a = g, f, e, (d + t1) % self.module, c, b, a, (t1 + t2) % self.module
            hash_values[0] = (a + hash_values[0]) % self.module
            hash_values[1] = (b + hash_values[1]) % self.module
            hash_values[2] = (c + hash_values[2]) % self.module
            hash_values[3] = (d + hash_values[3]) % self.module
            hash_values[4] = (e + hash_values[4]) % self.module
            hash_values[5] = (f + hash_values[5]) % self.module
            hash_values[6] = (g + hash_values[6]) % self.module
            hash_values[7] = (h + hash_values[7]) % self.module
            # print(f"hash: {format(hash_values[0],'x')}\t{format(hash_values[1],'x')}\t{format(hash_values[2],'x')}\t{format(hash_values[3],'x')}\t{format(hash_values[4],'x')}\t{format(hash_values[5],'x')}\t{format(hash_values[6],'x')}\t{format(hash_values[7],'x')}")
        hash_result = 0
        for i in range(8):
            # print(bin(hash_values[i]))
            hash_result = (hash_result << 32) + hash_values[i]
        return hash_result


if __name__ == '__main__':
    print(f"Enter message:")
    hash_func = SHA()
    data = input()
    message = bytearray(data.encode())
    L = hash_func.hash(message)
    print(f"length: {L.bit_length()}\nhash: {format(L,'X')}")
