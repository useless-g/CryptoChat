def gen_primes():
    D = {}
    q = 2

    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1


# primes_generator = gen_primes()
# with open("primes", "w") as f:
#     for _ in range(20_000_000):
#         if _ % 10000 == 0:
#             print(_)
#         f.write(f"{next(primes_generator)}\n")
# print(next(primes_generator))
# try:
#     with open("../rsa/primes", "r") as f:
#         first_20_000_000_primes_list = tuple(map(int, f.read().strip().split("\n")))
# except:
#     with open("./rsa/primes", "r") as f:
#         first_20_000_000_primes_list = tuple(map(int, f.read().strip().split("\n")))

first_100_primes_list = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                         31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                         73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
                         127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
                         179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
                         233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
                         283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
                         353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
                         419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
                         467, 479, 487, 491, 499, 503, 509, 521, 523, 541)
