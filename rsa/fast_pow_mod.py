from time import time


def fast_pow_mod(a: int, n: int, m: int) -> int:
    """
    :param a: number
    :param n: degree
    :param m: modulo
    :return: (a**n) % m
    """
    c = 1
    while n > 1:
        if n % 2 == 0:
            a = (a ** 2) % m
            n //= 2
        else:
            c = (c * a) % m
            n -= 1
    return c * a % m


if __name__ == "__main__":
    t = time()
    print((11 ** 2878063) % 3472094802933740923740923742322323237)
    print(time() - t)
    t = time()
    print(fast_pow_mod(11, 2878063, 3472094802933740923740923742322323237))
    print(time() - t)
