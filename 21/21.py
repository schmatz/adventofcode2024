from pathlib import Path
from itertools import permutations
from functools import cache
from typing import Literal


def parse_input_from_file(filename: str) -> list[str]:
    input_raw = (Path(__file__).parent / filename).read_text()
    input_lines = [line.strip() for line in input_raw.splitlines()]

    return input_lines


def do_problem(filename: str, inner_robot_count: int) -> int:
    numeric_keypad_codes = parse_input_from_file(filename)
    return calculate_shortest_manual_press_sequence_length(numeric_keypad_codes, inner_robot_count)
    
def calculate_sequence_complexity(code: str, shortest_sequence_length: int) -> int:
    return int(code[: len(code) - 1]) * shortest_sequence_length

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

assert len(next(iter(PREPROCESSED_NUMERIC_PATHS['A', '0']))) == 1
assert len(next(iter(PREPROCESSED_NUMERIC_PATHS['0', '2']))) == 1
assert len(next(iter(PREPROCESSED_NUMERIC_PATHS['2', '9']))) == 3
assert len(next(iter(PREPROCESSED_NUMERIC_PATHS['9', 'A']))) == 3

### Optimization should probably happen below this line

# Returns the path and the last position the robot was over
# Caching is probably a red herring but let's try it anyways
@cache
def _calculate_keypad_paths(code: str, initial_button: str, keypad_type: Literal["NUMERIC", "DIRECTIONAL"]) -> set[tuple[str, str]]:
    paths = PREPROCESSED_NUMERIC_PATHS if keypad_type == "NUMERIC" else PREPROCESSED_DIRECTIONAL_PATHS
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
    return _calculate_keypad_paths(code, initial_button, "NUMERIC")

def calculate_shortest_paths_directional_keypad(code: str, initial_button: str) -> set[tuple[str, str]]:
    return _calculate_keypad_paths(code, initial_button, "DIRECTIONAL")

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



def calculate_shortest_manual_press_sequence_length(codes: list[str], inner_robot_count: int) -> int:
    canonical_robot_hand_positions: dict[int, str] = {x: "A" for x in range(inner_robot_count)}

    shortest_sequences = []
    for code in codes:
        shortest_seq_found = None
        shortest_robot_hand_positions: dict[int, str] = {x: "A" for x in range(inner_robot_count)}

        inner_loop_paths = calculate_shortest_paths_numeric_keypad(code, "A")
        for numeric_seq, numeric_end_position in inner_loop_paths:
            print("processing inner loop seq", numeric_seq)
            assert numeric_end_position == "A" #All input keycodes end in A

            def explore_paths(robot_id: int, previous_seq: str, working_robot_hand_positions: dict[int, str]):
                nonlocal shortest_robot_hand_positions
                nonlocal shortest_seq_found

                #print(" ".join([str(i) for i in range(robot_id)]))
                if robot_id == inner_robot_count:
                    #print("Found seq", previous_seq)
                    if shortest_seq_found is None or len(previous_seq) < len(shortest_seq_found):
                        shortest_seq_found = previous_seq
                        shortest_robot_hand_positions = working_robot_hand_positions
                    return
                directional_paths = calculate_shortest_paths_directional_keypad(previous_seq, working_robot_hand_positions[robot_id])
                for robot_seq, robot_end_pos in directional_paths:
                    working_robot_hand_positions[robot_id] = robot_end_pos
                    explore_paths(robot_id + 1, robot_seq, working_robot_hand_positions)
                    
            explore_paths(0, numeric_seq, canonical_robot_hand_positions.copy())
        assert shortest_seq_found is not None

        canonical_robot_hand_positions = shortest_robot_hand_positions
                    
        shortest_sequences.append((code, shortest_seq_found))
        print(f"For code {code} there is the seq {shortest_seq_found} with length {len(shortest_seq_found)}")

    return sum(
        [calculate_sequence_complexity(short_seq[0], len(short_seq[1])) for short_seq in shortest_sequences]
    )

test1_solution = do_problem("test1.txt", 2)
print("Test1 case is", test1_solution)
assert test1_solution == 126384
problem_solution = do_problem("input.txt", 2)
print("problem solution is", problem_solution)
assert problem_solution == 184716

print("Starting crazy case")

crazy_solution = do_problem("input.txt", 25)
print("Crazy solution is", crazy_solution)
