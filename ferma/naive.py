import random
from math import ceil, sqrt
from time import time
from pyecf import LenstraAlgorithm

n = 155188576501293167865524267
algo = LenstraAlgorithm(n)
t = time()
factors = algo.factorize()  # отсортированный список делителей
print(factors)
print(time() - t)
from rsa.sieve import first_100_primes_list, first_20_000_000_primes_list


factors = set()
checked = set()


def check_first_primes(n):
    for divider in first_20_000_000_primes_list:
        if n % divider == 0:
            while n % divider == 0:
                n //= divider
            factors.add(divider)
    return n


def factorize(n):
    """
    Naive Fermat's Factorization method.
    Takes an integer n and return two factor in a tuple (c, d).
    """
    print(n)

    if n in checked or n <= 373587883:
        return []
    checked.add(n)

    # The method is valid only if n is odd
    # Check if n is odd

    if check_prime(n):
        factors.add(n)
        return [n]

    for divider in factors:
        while n % divider == 0:
            n //= divider

    start = ceil(sqrt(n))
    end = n
    a = start - 1
    while a < end:
        a += 1
        b_square = a ** 2 - n
        try:
            b = sqrt(b_square)
        except:
            continue
        if (ceil(b) == b) and (abs(b_square - a**2) == n):  # If b is a perfect square
            return factorize(int(a + b)) + factorize(int(a - b))
    return [n]


def check_prime(prime_candidate):
    for divisor in first_100_primes_list:
        if (prime_candidate % divisor == 0) and (divisor ** 2 <= prime_candidate):
            print(divisor)
            break
    # If no divisor found, return value
    else:
        return is_Miller_Rabin_test_passed(prime_candidate)


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
result = factorize(check_first_primes(280449854681501065584156165384199778092))
print(result)
print(factors)
print(sorted(list(factors)))
print(sorted(list(set(result))))
print(time() - t)
