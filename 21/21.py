from pathlib import Path
from itertools import permutations


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

# We can use a heuristic to generate the shortest paths, 

def get_all_shortest_paths(keypad_coords: dict[str, tuple[int,int]], initial_button: str, target_button: str) -> set[str]:
    initial_pos = keypad_coords[initial_button]
    target_pos = keypad_coords[target_button]
    forbidden_position = keypad_coords[FORBIDDEN_MARKER]

    x_difference = target_pos[0] - initial_pos[0]
    y_difference = target_pos[1] - initial_pos[1]

    manhattan_dist = abs(x_difference) + abs(y_difference)

    x_move = '>' if x_difference > 0 else '<'
    y_move = 'v' if y_difference > 0 else '^'

    element_string = x_move * abs(x_difference) + y_move * abs(y_difference)
    candidate_paths = set("".join(p) for p in permutations(element_string, r=manhattan_dist))
    # Filter paths that move to the X coord
    filtered_paths = set()
    for path in candidate_paths:
        current_coord = initial_pos
        should_add = True
        for move in path:
            move_tuple = DIRECTION_MOVES[move]
            x = current_coord[0] + move_tuple[0]
            y = current_coord[1] + move_tuple[1]
            if (x, y) == forbidden_position:
                should_add = False
                break
            current_coord = (x,y)
        if should_add:
            filtered_paths.add(path)
        
    return filtered_paths




PREPROCESSED_NUMERIC_PATHS = {
    (a, b): get_all_shortest_paths(NUMERIC_KEYPAD_COORDINATES, a, b)
    for a in NUMERIC_KEYPAD_COORDINATES.keys()
    for b in NUMERIC_KEYPAD_COORDINATES.keys()
    if a != b and a != FORBIDDEN_MARKER and b != FORBIDDEN_MARKER
}

PREPROCESSED_DIRECTIONAL_PATHS = {
    (a,b): get_all_shortest_paths(DIRECTIONAL_KEYPAD_COORDINATES, a, b)
    for a in DIRECTIONAL_KEYPAD_COORDINATES.keys()
    for b in DIRECTIONAL_KEYPAD_COORDINATES.keys()
    if a != b and a != FORBIDDEN_MARKER and b != FORBIDDEN_MARKER
}



# Preprocess the n^2 route table and then just do a table lookup during the algorithm
def calculate_numeric_example_shortest_paths(
    initial_button: str, target_button: str, 
) -> set[str]:
    return PREPROCESSED_NUMERIC_PATHS[(initial_button, target_button)]

def calculate_directional_example_shortest_path(
    initial_button: str, target_button: str,
) -> set[str]:
    return PREPROCESSED_DIRECTIONAL_PATHS[(initial_button, target_button)]


assert len(next(iter(calculate_numeric_example_shortest_paths('A', '0')))) == 1
assert len(next(iter(calculate_numeric_example_shortest_paths('0', '2')))) == 1
assert len(next(iter(calculate_numeric_example_shortest_paths('2', '9')))) == 3
assert len(next(iter(calculate_numeric_example_shortest_paths('9', 'A')))) == 3

# Returns the path and the last position the robot was over
def _calculate_keypad_paths(code: str, initial_button: str, paths: dict[tuple[str, str], set[str]]) -> set[tuple[str, str]]:
    possible_paths: set[tuple[str, str]] = set()

    def explore(current_code: str, current_path: str, current_button: str):
        nonlocal possible_paths
        if len(current_code) == 0:
            possible_paths.add((current_path, current_button))
            return

        current_char = current_code[0]
        rest = current_code[1:]
        if current_char != current_button:
            candidate_paths = paths[(current_button, current_char)]
            for path in candidate_paths:
                explore(rest, current_path + path + "A", current_char)
        else:
            explore(rest, current_path + "A", current_char)
    

    explore(code, "", initial_button)

    return possible_paths


def calculate_shortest_paths_numeric_keypad(code: str, initial_button: str) -> set[tuple[str,str]]:
    return _calculate_keypad_paths(code, initial_button, PREPROCESSED_NUMERIC_PATHS)

def calculate_shortest_paths_directional_keypad(code: str, initial_button: str) -> set[tuple[str, str]]:
    return _calculate_keypad_paths(code, initial_button, PREPROCESSED_DIRECTIONAL_PATHS)

seq_029a = calculate_shortest_paths_numeric_keypad("029A", "A")
good_numeric_answer = "<A^A>^^AvvvA"
assert good_numeric_answer in {s[0] for s in seq_029a}

# Needs debugging
seqs_robot_a_029a = calculate_shortest_paths_directional_keypad(good_numeric_answer, "A")
good_a_answer = "v<<A>>^A<A>AvA<^AA>A<vAAA>^A"
assert good_a_answer in {s[0] for s in seqs_robot_a_029a}

seqs_robot_b_029a = calculate_shortest_paths_directional_keypad(good_a_answer, "A")
good_b_answer = "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A"
assert good_b_answer in {s[0] for s in seqs_robot_b_029a}



def calculate_shortest_manual_press_sequence_length(codes: list[str]) -> int:
    # These should only be updated at the end of each code
    numeric_keypad_robot_pos = "A"
    robot_a_pos = "A"
    robot_b_pos = "A"

    shortest_sequences = []
    for code in codes:
        shortest_seq_found = None
        shortest_robot_a_pos = None
        shortest_robot_b_pos = None
        for numeric_seq, numeric_end_position in calculate_shortest_paths_numeric_keypad(code, numeric_keypad_robot_pos):
            assert numeric_end_position == "A" #All input keycodes end in A

            for robot_a_seq, robot_a_end_pos in calculate_shortest_paths_directional_keypad(numeric_seq, robot_a_pos):
                for robot_b_seq, _ in calculate_shortest_paths_directional_keypad(robot_a_seq, robot_b_pos):
                    if shortest_seq_found is None or len(robot_b_seq) < len(shortest_seq_found):
                        shortest_seq_found = robot_b_seq
                        shortest_robot_a_pos = robot_a_end_pos
                        shortest_robot_b_pos = robot_b_pos
        assert shortest_robot_a_pos is not None and shortest_robot_b_pos is not None and shortest_seq_found is not None
        robot_a_pos = shortest_robot_a_pos
        robot_b_pos = shortest_robot_b_pos
                    
        shortest_sequences.append((code, shortest_seq_found))
        print(f"For code {code} there is the seq {shortest_seq_found} with length {len(shortest_seq_found)}")

    return sum(
        [calculate_sequence_complexity(short_seq[0], len(short_seq[1])) for short_seq in shortest_sequences]
    )

problem_solution = do_problem("input.txt")
print("problem solution is", problem_solution)
assert do_problem("test1.txt") == 126384

# print(do_problem("input.txt"))
