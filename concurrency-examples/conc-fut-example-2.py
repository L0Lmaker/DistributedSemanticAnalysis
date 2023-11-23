import concurrent.futures
import math
import time

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
]


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.sqrt(n))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


def main():
    start_time = time.time()  # Capture start time
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print(f"{number} is prime: {prime}")
    end_time = time.time()  # Capture end time
    print(f"Runtime of the program is {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
