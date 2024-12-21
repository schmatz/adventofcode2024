from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush
from collections import Counter
from dataclasses import dataclass


def parse_input_from_file(filename: str) -> list[str]:
    input_raw = (Path(__file__).parent / filename).read_text()
    input_lines = [line.strip() for line in input_raw.splitlines()]

    return input_lines


def do_problem(filename: str) -> int:
    numeric_keypad_codes = parse_input_from_file(filename)
    return calculate_shortest_manual_press_sequence_length(numeric_keypad_codes)
    


def calculate_sequence_complexity(code: str, shortest_sequence_length: int) -> int:
    return int(code[: len(code) - 1]) * shortest_sequence_length

### Numeric Keypad 1
# 789
# 456
# 123
#  0A

# A presses button

# Cannot push buttons directly, has keypad 2 to control robot A to press numeric keypad 1
#  ^A
# <v>

# Initially robotic arm is pointed at A bottom right on keypad 1


# To press 029A on keypad 1, robot A needs < to move to 0 on numeric keypad 1, A to press 0, ^A to press 2, >^^A to press 9, vvvA to press arm to A button
# There are three shortest sequences, <A^A>^^AvvvA, <A^A^>^AvvvA, and <A^A^^>AvvvA. (basically navigating the manhattan grid to get X up and Y left on the 0 to 9 move)
# These are presses on keypad 2 (directional) to control robot A to press on keypad 1

# We cannot directly press keypad 2. Robot B will press keypad 2 (directional) to control robot A, who will then press keypad 1.
# Robot B originally is pointed at the upper-right-hand-corner A on keypad 2 (directional).

# Similarly, we cannot directly control Robot B. We need Robot C to press keypad 3  (directional) to control Robot 2. Otherwise same as Robot B and keypad 2.

# A shortest sequence (out of multiple) for robot C is v<<A>>^A<A>AvA<^AA>A<vAAA>^A to press on keypad 3.

# We ourselves will press keypad 4 (directional) to control robot C.
# Possible shortest sequence is <vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A

# So in summary, the inputs are
# Directional Keypad 4 (pressed by us)      <vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A
# Directional Keypad 3 (pressed by robot C) v<<A>>^A<A>AvA<^AA>A<vAAA>^A
# Directional Keypad 2 (pressed by robot B) <A^A>^^AvvvA
# Numeric     Keypad 1 (pressed by robot A) 029A

# All robot start aiming at A.
# Robots can never aim at the gap on the controls, even for a moment. So no lower left corner on numeric keypad or upper right on directional keypad

# For test case, here is a shortest sequence that works:
"""
029A: <vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A
980A: <v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A
179A: <v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A
456A: <v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A
379A: <v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A
"""

# We need to find the shortest sequence, then compute its complexity. Multiply:
# * Length of shortest sequence of final button presses (for 029A this is 68)
# * Numeric part of the code (for 029A it is 29)
# 029A has 68*29, 980A has 60 * 980, 179A has 68 * 179, 456A has 64 * 456, and 379 has 64 * 369.
# Sum of products is 126384

FORBIDDEN_MARKER = "X"

NUMERIC_KEYPAD_COORDINATES: dict[str, tuple[int, int]] = {
    "7": (0, 0),
    "8": (1, 0),
    "9": (2, 0),
    "4": (0, 1),
    "5": (1, 1),
    "6": (2, 1),
    "1": (0, 2),
    "2": (1, 2),
    "3": (2, 2),
    FORBIDDEN_MARKER: (0, 3),
    "0": (1, 3),
    "A": (2, 3),
}

DIRECTIONAL_KEYPAD_COORDINATES: dict[str, tuple[int, int]] = {
    FORBIDDEN_MARKER: (0, 0),
    "^": (1, 0),
    "A": (2, 0),
    "<": (0, 1),
    "v": (1, 1),
    ">": (2, 1),
}

DIRECTION_MOVES: dict[str, tuple[int, int]] = {
    "^": (0, -1),
    "v": (0, 1),
    "<": (-1, 0),
    ">": (1, 0),
}

def preprocess_paths_slow(
    keypad_coords: dict[str, tuple[int, int]], initial_button: str, target_button: str
) -> str:
    initial_pos = keypad_coords[initial_button]
    target_pos = keypad_coords[target_button]
    forbidden_position = keypad_coords["X"]

    visited: set[tuple[int, int]] = set()
    predecessors: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

    distances: dict[tuple[int, int], int] = {
        coord: 1000 for coord in keypad_coords.values() if coord != forbidden_position
    }
    distances[initial_pos] = 0
    pq: list[tuple[int, tuple[int, int]]] = [(0, initial_pos)]
    heapify(pq)

    while pq:
        current_distance, pos = heappop(pq)
        if pos in visited:
            continue
            
        assert pos != forbidden_position

        visited.add(pos)

        for direction_letter, movement_coord in DIRECTION_MOVES.items():
            next_coord = (pos[0] + movement_coord[0], pos[1] + movement_coord[1])

            if next_coord not in distances:
                continue

            assert next_coord != forbidden_position

            tentative_distance = current_distance + 1

            if tentative_distance < distances[next_coord]:
                distances[next_coord] = tentative_distance
                predecessors[next_coord] = (pos, direction_letter)
                heappush(pq, (tentative_distance, next_coord))

    example_path = ""
    current_node = target_pos
    while current_node in predecessors:
        current_node, d = predecessors[current_node]
        example_path += d
    return example_path[::-1]



PREPROCESSED_NUMERIC_PATHS = {
    (a, b): {preprocess_paths_slow(NUMERIC_KEYPAD_COORDINATES, a, b)}
    for a in NUMERIC_KEYPAD_COORDINATES.keys()
    for b in NUMERIC_KEYPAD_COORDINATES.keys()
    if a != b and a != FORBIDDEN_MARKER and b != FORBIDDEN_MARKER
}

PREPROCESSED_DIRECTIONAL_PATHS = {
    (a,b): {preprocess_paths_slow(DIRECTIONAL_KEYPAD_COORDINATES, a, b)}
    for a in DIRECTIONAL_KEYPAD_COORDINATES.keys()
    for b in DIRECTIONAL_KEYPAD_COORDINATES.keys()
    if a != b and a != FORBIDDEN_MARKER and b != FORBIDDEN_MARKER
}


# Preprocess the n^2 route table and then just do a table lookup during the algorithm
def calculate_numeric_example_shortest_path(
    initial_button: str, target_button: str, 
) -> set[str]:
    return PREPROCESSED_NUMERIC_PATHS[(initial_button, target_button)]

def calculate_directional_example_shortest_path(
    initial_button: str, target_button: str,
) -> set[str]:
    return PREPROCESSED_DIRECTIONAL_PATHS[(initial_button, target_button)]


assert len(next(iter(calculate_numeric_example_shortest_path('A', '0')))) == 1
assert len(next(iter(calculate_numeric_example_shortest_path('0', '2')))) == 1
assert len(next(iter(calculate_numeric_example_shortest_path('2', '9')))) == 3
assert len(next(iter(calculate_numeric_example_shortest_path('9', 'A')))) == 3

# Returns the path and the last position the robot was over
def _calculate_keypad_path(code: str, initial_button: str, paths: dict[tuple[str, str], set[str]]) -> set[tuple[str, str]]:
    example_shortest_path = ""
    current_button = initial_button
    for char in code:
        if char != current_button:
            example_shortest_path += next(iter(paths[(current_button, char)]))
        example_shortest_path += "A"
        current_button = char 
    return {(example_shortest_path, current_button)}


def calculate_shortest_path_numeric_keypad(code: str, initial_button: str) -> set[tuple[str,str]]:
    return _calculate_keypad_path(code, initial_button, PREPROCESSED_NUMERIC_PATHS)

def calculate_shortest_path_directional_keypad(code: str, initial_button: str) -> set[tuple[str, str]]:
    return _calculate_keypad_path(code, initial_button, PREPROCESSED_DIRECTIONAL_PATHS)

seq_029a = next(iter(calculate_shortest_path_numeric_keypad("029A", "A")))
assert len(seq_029a[0]) == len("<A^A>^^AvvvA")

# Known good
print("Numeric Keypad seq", seq_029a)

# Needs debugging
seq_robot_a_029a = next(iter(calculate_shortest_path_directional_keypad(seq_029a[0], "A")))
assert len(seq_robot_a_029a[0]) == len("v<<A>>^A<A>AvA<^AA>A<vAAA>^A")
print("ROBOT A")
print("YOU OUTPUTTED:", seq_robot_a_029a[0])
print("KNOWN GOOD ANSWER", "v<<A>>^A<A>AvA<^AA>A<vAAA>^A")
seq_robot_b_029a = next(iter(calculate_shortest_path_directional_keypad(seq_robot_a_029a[0], "A")))
print("ROBOT B")
print("YOU OUTPUTTED:", seq_robot_b_029a[0])
print("KNOWN GOOD ANSWER", "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A")
assert len(seq_robot_b_029a[0]) == len("<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A")

def calculate_shortest_manual_press_sequence_length(codes: list[str]) -> int:
    numeric_keypad_robot_pos = "A"
    robot_a_pos = "A"
    robot_b_pos = "A"

    shortest_sequences = []
    for code in codes:
        # Robot operating this one 
        numeric_seq, numeric_keypad_pos = calculate_shortest_path_numeric_keypad(code, numeric_keypad_robot_pos)
        assert numeric_keypad_pos == "A" #All input keycodes end in A
        # Our two robots doing directional stuff
        robot_a_seq, robot_a_pos = calculate_shortest_path_directional_keypad(numeric_seq, robot_a_pos)
        robot_b_seq, robot_b_pos = calculate_shortest_path_directional_keypad(robot_a_seq, robot_b_pos)
        # We are inputting robot b seq
        shortest_sequences.append((code, robot_b_seq))
        print(f"For code {code} there is the seq {robot_b_seq} with length {len(robot_b_seq)}")

    return sum(
        [calculate_sequence_complexity(short_seq[0], len(short_seq[1])) for short_seq in shortest_sequences]
    )

problem_solution = do_problem("test1.txt")
print("problem solution is", problem_solution)
assert problem_solution == 126384

# print(do_problem("input.txt"))
