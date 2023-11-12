from typing import Tuple


def euclid_extended(a: int, b: int) -> Tuple[int, int, int]:
    x, xx, y, yy = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, xx = xx, x - xx * q
        y, yy = yy, y - yy * q
    return x, y, a


def find_inverse(a: int, m: int) -> int:
    """
    :param a: number, which inverse we search for
    :param m: modulo
    :return: b - inverse of a (a*b === 1 (mod m))
    """
    return euclid_extended(a, m)[0]
