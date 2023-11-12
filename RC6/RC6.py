import json as js
from math import e, sqrt, ceil

def ROTL(x, y, w):
    return (x << (y & (w - 1))) | (x >> (w - (y & (w - 1))))

def ROTR(x, y, w):
    return (x >> (y & (w - 1))) | (x << (w - (y & (w - 1))))  # try % w instead of & w-1


class RC5:

    def __init__(self):
        with open("./params.cfg", "r") as f:
            params = js.load(f)
        self.w = int(params["w"])
        self.r = int(params["r"])
        self.key = int(params["key"])
        key = []
        while self.key:
            key.append(self.key % 256)
            self.key //= 256
        self.key = key[::-1]
        self.modulo = 2 ** self.w
        self.S = []
        self.fill_S()

    def fill_S(self):
        Odd = lambda x: int(x) if int(x) % 2 else int(x) + 1
        golden_ratio = (1 + sqrt(5)) / 2
        P = Odd((e - 2) * self.modulo)  # correct
        Q = Odd((golden_ratio - 1) * self.modulo)  # correct
        b = len(self.key)  # correct
        u = ceil(self.w / 8)  # correct
        c = ceil(b / u)  # correct
        t = 2 * (self.r + 1)  # correct
        if b == c == 0:
            c = 1
        L = [0 for _ in range(c)]

        for i in range(b - 1, -1, -1):
            L[int(i / u)] = self.add_modulo(L[int(i / u)] << 8, self.key[i])

        self.S = [0 for _ in range(t)]
        self.S[0] = P
        for i in range(1, t):
            self.S[i] = (self.S[i - 1] + Q) % self.modulo

        A = B = i = j = 0

        for _ in range(3 * max(t, c)):
            A = self.S[i] = ROTL(self.add_modulo(self.S[i], (A + B) % self.modulo), 3, self.w) % self.modulo
            B = L[j] = ROTR(self.add_modulo(L[j], self.add_modulo(A, B)), self.add_modulo(A, B), self.w) % self.modulo

            i = (i + 1) % t
            j = (j + 1) % c

    def add_modulo(self, a, b):
        return (a + b) % self.modulo

    def sub_modulo(self, a, b):
        return (a - b) % self.modulo

    def encrypt(self, text):
        A, B = self.text_to_AB(text)  # A: 1919252337    B:  1919252337
        A = self.add_modulo(A, self.S[0])
        B = self.add_modulo(B, self.S[1])
        for i in range(1, self.r + 1):
            A = (ROTL(A ^ B, B, self.w) + self.S[2 * i]) % self.modulo
            B = (ROTR(B ^ A, A, self.w) + self.S[2 * i + 1]) % self.modulo
        return self.AB_to_text(A, B)

    def decrypt(self, text):
        A, B = self.text_to_AB(text)  # A:476140826    B: 3922915879
        for i in range(self.r, 0, -1):
            B = (ROTR(self.sub_modulo(B, self.S[2 * i + 1]), A, self.w) % self.modulo) ^ A
            A = (ROTR(self.sub_modulo(A, self.S[2 * i]), B, self.w) % self.modulo) ^ B
        B = self.sub_modulo(B, self.S[1])
        A = self.sub_modulo(A, self.S[0])
        return self.AB_to_text(A, B)

    def text_to_AB(self, text):
        A = sum([ord(text[i]) << (8 * i) for i in range(ceil(self.w / 8) - 1, -1, -1)])
        B = sum([ord(text[i]) << (8 * (i - ceil(self.w / 8))) for i in
                 range(ceil(self.w / 8) * 2 - 1, ceil(self.w / 8) - 1, -1)])
        return A, B

    def AB_to_text(self, A, B):  #
        res = ''
        while A:
            res += chr(A % 256)
            A //= 256
        while B:
            res += chr(B % 256)
            B //= 256
        return res


if __name__ == "__main__":
    rc = RC5()
    text = 'qwerqwer'
    # AB = rc.text_to_AB(text)
    # print(AB)
    # print(rc.AB_to_text(AB[0], AB[1]))
    encrypted = rc.encrypt(text)  # ''
    print(encrypted)
    decrypted = rc.decrypt(encrypted)
    print(decrypted)
