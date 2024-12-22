from pathlib import Path
from dataclasses import dataclass
import re
import numpy as np

type XYData = tuple[int, int]


@dataclass
class ProblemSpec:
    ButtonA: XYData
    ButtonB: XYData
    Prize: XYData


input_text = (Path(__file__).parent / "input.txt").read_text()
input_lines = input_text.splitlines()


def get_coord_from_line(line: str) -> XYData:
    matches = re.search(r"X[=+](\d+).+Y[=+](\d+)", line)
    assert matches is not None

    assert len(matches.groups()) == 2

    return (int(matches.group(1)), int(matches.group(2)))


grid_specs: list[ProblemSpec] = []
assert (len(input_lines) + 1) % 4 == 0
for i in range((len(input_lines) + 1) // 4):
    aLine = input_lines[i * 4]
    bLine = input_lines[i * 4 + 1]
    prizeLine = input_lines[i * 4 + 2]

    spec = ProblemSpec(
        get_coord_from_line(aLine),
        get_coord_from_line(bLine),
        get_coord_from_line(prizeLine),
    )
    grid_specs.append(spec)


def get_combo_for_winning(spec: ProblemSpec) -> XYData | None:
    button_a_x = spec.ButtonA[0]
    button_a_y = spec.ButtonA[1]
    button_b_x = spec.ButtonB[0]
    button_b_y = spec.ButtonB[1]
    prize_x = spec.Prize[0]
    prize_y = spec.Prize[1]
    # Dumb approach but let's try
    for a in range(101):
        for b in range(101):
            test_x = a * button_a_x + b * button_b_x
            test_y = a * button_a_y + b * button_b_y
            if test_x == prize_x and test_y == prize_y:
                return (a, b)
            if test_x > prize_x or test_y > test_y:
                break  # Go onto the next outer loop

    return None


def optimized_int_combo(spec: ProblemSpec) -> tuple[int, int] | None:
    buttons = np.array(
        [[spec.ButtonA[0], spec.ButtonB[0]], [spec.ButtonA[1], spec.ButtonB[1]]]
    )
    prize = np.array(list(spec.Prize))

    solution = np.linalg.solve(buttons, prize)

    # This was way harder than it should have been...
    is_a_int = np.isclose(solution[0], round(solution[0]), rtol=0, atol=1e-04)
    is_b_int = np.isclose(solution[1], round(solution[1]), rtol=0, atol=1e-04)

    if not (is_a_int and is_b_int):
        return None

    return (int(round(solution[0])), int(round(solution[1])))


OFFSET = 10000000000000
altered_specs = [
    ProblemSpec(
        spec.ButtonA, spec.ButtonB, (spec.Prize[0] + OFFSET, spec.Prize[1] + OFFSET)
    )
    for spec in grid_specs
]

total_tokens = 0
for spec in altered_specs:
    winning_combo = optimized_int_combo(spec)
    if not winning_combo:
        continue
    total_tokens += winning_combo[0] * 3 + winning_combo[1]

print("Total tokens", total_tokens)
