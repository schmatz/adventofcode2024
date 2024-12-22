import sys

from pathlib import Path


def find_horizontal_instances(grid: list[list[str]], search_term: str) -> int:
    found = 0
    for line in grid:
        for i in range(0, len(line) - len(search_term) + 1):
            substring = "".join(line[i : i + len(search_term)])
            if substring == search_term or substring[::-1] == search_term:
                found += 1
    return found


def find_diagonal_instances_left_to_right(
    grid: list[list[str]], search_term: str
) -> int:
    found = 0
    line_length = len(grid[0])
    for x_start in range(0, line_length - len(search_term) + 1):
        for y_start in range(0, line_length - len(search_term) + 1):
            chars = []
            for i in range(len(search_term)):
                chars.append(grid[x_start + i][y_start + i])
            substring = "".join(chars)
            if substring == search_term or substring[::-1] == search_term:
                found += 1

    return found


def solve_problem_1(file_contents: str, search_term: str):
    lines = file_contents.split()
    num_lines = len(lines)
    line_lengths = [len(line) for line in lines]
    assert all([length == line_lengths[0] for length in line_lengths])
    line_length = line_lengths[0]

    print(f"Puzzle dimensions: x {line_length}, y {num_lines}")
    assert line_length == num_lines

    char_grid = [list(line) for line in lines]

    horizontal_found = find_horizontal_instances(char_grid, search_term)
    print(f"Horizontal: {horizontal_found}")

    # TODO: Figure out how this works
    transposed = list(map(list, zip(*char_grid)))
    vertical_instances_found = find_horizontal_instances(transposed, search_term)
    print(f"Vertical: {vertical_instances_found}")

    left_to_right_diag = find_diagonal_instances_left_to_right(char_grid, search_term)
    print(left_to_right_diag)
    flipped = [line[::-1] for line in char_grid]
    right_to_left_diag = find_diagonal_instances_left_to_right(flipped, search_term)
    print(right_to_left_diag)

    total_occurrences = (
        horizontal_found
        + vertical_instances_found
        + left_to_right_diag
        + right_to_left_diag
    )
    print(f"Total occurrences: {total_occurrences}")


def solve_problem_2(file_contents: str, search_term: str):
    lines = file_contents.split()
    char_grid = [list(line) for line in lines]

    found = 0

    # TODO: Check off by one
    for a_center_x in range(1, len(char_grid) - 1):
        for a_center_y in range(1, len(char_grid) - 1):
            center = char_grid[a_center_x][a_center_y]
            if center != "A":
                continue
            left_diag_corners = set(
                (
                    char_grid[a_center_x - 1][a_center_y - 1],
                    char_grid[a_center_x + 1][a_center_y + 1],
                )
            )
            if "M" not in left_diag_corners or "S" not in left_diag_corners:
                continue
            right_diag_corners = set(
                (
                    char_grid[a_center_x - 1][a_center_y + 1],
                    char_grid[a_center_x + 1][a_center_y - 1],
                )
            )
            if "M" not in right_diag_corners or "S" not in right_diag_corners:
                continue
            found += 1

    print(f"Found {found} X-MASes")


if __name__ == "__main__":
    p = Path(sys.argv[1])
    file_contents = p.read_text()

    solve_problem_1(file_contents, "XMAS")
    solve_problem_2(file_contents, "MAS")
