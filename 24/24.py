from pathlib import Path
from itertools import permutations
from functools import cache
from typing import Literal, cast
from collections import deque, defaultdict, Counter
import re

def do_problem_part_2(filename: str) -> int:
    input = (Path(__file__).parent / filename).read_text().splitlines()
    gate_values = {}
    operations = []
    for line in input:
        if ":" in line:
            name, value = line.split(":")
            gate_values[name] = int(value)
        else:
            matches = re.search(r"(\w+) (\w+) (\w+) -> (\w+)", line)
            if matches:
                operations.append(matches.groups())

    number_width = len(gate_values) // 2
    assert all([k.startswith("x") or k.startswith("y") for k in gate_values.keys()])
    x_values = [k for k in reversed(sorted(gate_values.keys())) if k.startswith("x")]
    y_values = [k for k in reversed(sorted(gate_values.keys())) if k.startswith("y")]
    assert len(x_values) == len(y_values)
    x_in_binary = int("".join(str(gate_values[x_value]) for x_value in x_values), 2)
    y_in_binary = int("".join(str(gate_values[y_value]) for y_value in y_values), 2)
    target_sum = x_in_binary + y_in_binary

    target_z_values = [int(bin(target_sum)[2:][i]) for i in range(number_width + 1)]
    actual_z_values = [int(bin(do_problem_part_1(filename))[2:][i]) for i in range(number_width + 1)]

    print(target_z_values)
    print(actual_z_values)

    # Go through the number from LSB to MSB and figure out if the value is incorrect

    
    return 0

def simulate_operations(operations: list[tuple[str, str, str, str]], gate_values: dict[str, int]) -> dict[str, int]:
    while operations:
        for operation in operations:
            wire_1 = operation[0]
            wire_2 = operation[2]
            if wire_1 not in gate_values or wire_2 not in gate_values:
                continue

            operations.remove(operation)

            if operation[1] == "AND":
                gate_values[operation[3]] = gate_values[wire_1] & gate_values[wire_2]
            elif operation[1] == "OR":
                gate_values[operation[3]] = gate_values[wire_1] | gate_values[wire_2]
            elif operation[1] == "XOR":
                gate_values[operation[3]] = gate_values[wire_1] ^ gate_values[wire_2]
            else:
                raise ValueError(f"Unknown operation: {operation[1]}")
        
    return gate_values


def do_problem_part_1(filename: str) -> int:
    input = (Path(__file__).parent / filename).read_text().splitlines()
    gate_values = {}
    operations = []
    for line in input:
        if ":" in line:
            name, value = line.split(":")
            gate_values[name] = int(value)
        else:
            matches = re.search(r"(\w+) (\w+) (\w+) -> (\w+)", line)
            if matches:
                operations.append(matches.groups())
    
    gate_values = simulate_operations(operations, gate_values)
    
    z_values = {k: v for k, v in gate_values.items() if k.startswith("z")}
    # sort the z_values
    z_value_sorted_keys = list(reversed(sorted(z_values.keys())))
    # join them to a binary string
    binary_string = "".join(str(z_values[k]) for k in z_value_sorted_keys)
    # convert to int
    return int(binary_string, 2)
    

# Monkey only sells after looking for a specific sequence of four consecutive changes in price
# First price has no change due to lack of comparison
# Find the highest 4-seq to get the most bananas across all buyers
# Each buyer gets 2000 price changes


print("part 1 answer", do_problem_part_1("input.txt"))
print("part 2 answer", do_problem_part_2("input.txt"))