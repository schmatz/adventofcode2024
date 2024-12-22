from pathlib import Path
from itertools import permutations
from functools import cache
from typing import Literal
from collections import deque, defaultdict, Counter

# Sell hiding spots
# prices are only pseudorandom
# Each buyer produces pseudorandom numbers, each secret derived from previous
# Secret number follows process:
# 1. Multiply secret result into 64, then "mix" and "prune"
# 2. Divde number by 32, ROUND DOWN, then "mix" and "prune"
# 3. Multiply secret by 2048, then mix and prune

# To mix, bitwise XOR of two values
# TO prune, mod 16777216, then result is of that operation

# Then, next secret number in a sequence

# next 10 secret numbers of 123 would be


def mix(a: int, b: int) -> int:
    return a ^ b


# Essentially get lower 23 binary digits
def prune(a: int) -> int:
    return a % 16777216  # (2 ^ 24)


def get_next_secret_number(secret: int) -> int:
    secret = prune(mix((secret * 64), secret))
    secret = prune(mix((secret // 32), secret))
    secret = prune(mix((secret * 2048), secret))
    return secret


def get_price_from_secret_number(secret: int) -> int:
    return secret % 10


assert get_next_secret_number(123) == 15887950
assert get_price_from_secret_number(123) == 3
assert get_next_secret_number(15887950) == 16495136
assert get_price_from_secret_number(15887950) == 0
assert get_next_secret_number(16495136) == 527345
assert get_price_from_secret_number(16495136) == 6


def parse_input_from_file(filename: str) -> list[int]:
    input_raw = (Path(__file__).parent / filename).read_text()
    return [int(line) for line in input_raw.splitlines()]


def calculate_sequence_prices(secret: int) -> dict[tuple[int, ...], int]:
    change_buffer: deque[int] = deque([], maxlen=4)

    price_seq_dict: defaultdict[tuple[int, ...], int] = defaultdict(lambda: 0)

    old_secret = secret
    for i in range(2000):
        new_secret = get_next_secret_number(old_secret)
        new_price = get_price_from_secret_number(new_secret)
        old_price = get_price_from_secret_number(old_secret)
        price_difference = new_price - old_price
        change_buffer.append(price_difference)
        if tuple(change_buffer) not in price_seq_dict and len(change_buffer) == 4:
            price_seq_dict[tuple(change_buffer)] = new_price

        old_secret = new_secret

    return price_seq_dict


def do_problem(filename: str) -> int:
    input = parse_input_from_file(filename)

    secret_sum = 0
    price_counter: Counter[tuple[int, ...], int] = Counter()
    # Each monkey can only sell one banana, and so we want to do a
    for secret_num in input:
        new_secret = secret_num
        for i in range(2000):
            new_secret = get_next_secret_number(new_secret)
        price_counter.update(calculate_sequence_prices(secret_num))

        secret_sum += new_secret

    print(price_counter.most_common()[0][1])

    return secret_sum


# Monkey only sells after looking for a specific sequence of four consecutive changes in price
# First price has no change due to lack of comparison
# Find the highest 4-seq to get the most bananas across all buyers
# Each buyer gets 2000 price changes


print("part 1 answer", do_problem("input.txt"))
