from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush

type Tile = Literal["#", ".", "S", "E"]
type Coordinate = tuple[int, int]
type Movement = Literal["^", "v", ">", "<"]

type Grid = list[list[Tile]]


def find_char_in_grid(char: Tile, grid: Grid) -> Coordinate:
    tile_pos = None
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == char:
                tile_pos = (x, y)
                break
        if tile_pos is not None:
            break

    if tile_pos is None:
        raise AssertionError("robot needs to be in grid")

    return tile_pos


def parse_input_from_file(file: Path) -> Grid:
    input_raw = file.read_text()

    input_lines = [line.strip() for line in input_raw.splitlines()]

    grid = [list(line) for line in input_lines]

    cast_grid = cast(Grid, grid)

    return cast_grid


def print_grid(grid: list[list[Tile]], coords: set[Coordinate]):
    output_str = ""
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if (x, y) in coords:
                output_str += "O"
            else:
                output_str += xchar
        output_str += "\n"
    print(output_str)
    #(Path(__file__).parent / "output.txt").write_text(output_str)

def print_grid_cost(grid: list[list[Tile]], distances: dict[Coordinate, int]):
    output_str = ""
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if (x, y) in distances:
                output_str += f'{distances[(x,y)]:06} '
            else:
                output_str += xchar * 6 + ' '
        output_str += "\n"
    (Path(__file__).parent / "output.txt").write_text(output_str)

def get_relative_coord(pos: Coordinate, movement: Movement) -> Coordinate:
    match movement:
        case "^":
            return (pos[0], pos[1] - 1)
        case "v":
            return (pos[0], pos[1] + 1)
        case "<":
            return (pos[0] - 1, pos[1])
        case ">":
            return (pos[0] + 1, pos[1])


MOVEMENTS_SET: set[Movement] = set(["^", "v", ">", "<"])


def get_valid_moves(previousMovement: Movement) -> list[Movement]:
    match previousMovement:
        case ">":
            return list(MOVEMENTS_SET - set(["<"]))
        case "^":
            return list(MOVEMENTS_SET - set(["v"]))
        case "<":
            return list(MOVEMENTS_SET - set([">"]))
        case "v":
            return list(MOVEMENTS_SET - set(["^"]))
        
def reverse_direction(mov: Movement) -> Movement:
    match mov:
        case ">":
            return '<'
        case "^":
            return 'v'
        case "<":
            return '>'
        case 'v':
            return '^'


INFINITY_VALUE = 1_000_000_000_000_000_000
DIRECTIONS: set[Movement] = {"^", ">", "v", "<"}


def dijkstras_algorithm(grid: Grid) -> int:
    distances: dict[tuple[Coordinate, Movement], int] = {}

    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == "#":
                continue
            else:
                for direction in DIRECTIONS:
                    distances[((x, y), direction)] = INFINITY_VALUE

    initial_player_position = find_char_in_grid("S", grid)
    distances[(initial_player_position, ">")] = 0
    pq: list[tuple[int, Coordinate, Movement]] = [(0, initial_player_position, ">")]
    heapify(pq)

    visited: set[tuple[Coordinate, Movement]] = set()

    while pq:
        current_distance, pos, previousMovement = heappop(pq)
        if (pos, previousMovement) in visited:
            continue

        visited.add((pos, previousMovement))

        for movement in get_valid_moves(previousMovement):
            if movement == previousMovement:
                next_tile_coord = get_relative_coord(pos, movement)
            else:
                next_tile_coord = pos

            if (next_tile_coord, movement) not in distances:
                continue

            tentative_distance = None
            if movement == previousMovement:
                tentative_distance = current_distance + 1
            else:
                tentative_distance = current_distance + 1000

            if tentative_distance < distances[(next_tile_coord, movement)]:
                distances[(next_tile_coord, movement)] = tentative_distance
                heappush(pq, (tentative_distance, next_tile_coord, movement))


    print(get_all_coordinates_in_shortest_path(grid, distances))

    return min(
        [
            distances[(find_char_in_grid("E", grid), direction)]
            for direction in DIRECTIONS
        ]
    )


def get_all_coordinates_in_shortest_path(
    grid: Grid, distances: dict[tuple[Coordinate, Movement], int]
) -> int:
    print_grid_cost(grid, {x[0]: y for x,y in distances.items()})
    e_location = find_char_in_grid("E", grid)
    shortest_path_dist = min(
        [distances[(e_location, direction)] for direction in DIRECTIONS]
    )
    visited: set[tuple[Coordinate, Movement]] = set()

    starting_directions = [
        (e_location, direction)
        for direction in DIRECTIONS
        if distances[(e_location, direction)] == shortest_path_dist
    ]

    def explore_backwards(pos: Coordinate, previousMovement: Movement):
        if (pos, previousMovement) in visited:
            return
        visited.add((pos, previousMovement))

        candidate_dists: dict[tuple[Coordinate, Movement], int] = {}
        for movement in get_valid_moves(previousMovement):
            if movement == previousMovement:
                next_tile_coord = get_relative_coord(pos, reverse_direction(movement))
            else:
                next_tile_coord = pos

            if (next_tile_coord, movement) not in distances:
                continue

            candidate_dists[(next_tile_coord, movement)] = distances[(next_tile_coord, movement)]
        
        min_dist = min(candidate_dists.values())
        print(len(candidate_dists))
        for potential_move in candidate_dists:
            if candidate_dists[potential_move] != min_dist:
                continue
            explore_backwards(potential_move[0], potential_move[1])

    for direction in starting_directions:
        explore_backwards(direction[0], direction[1])
    visited_coords = set((coord[0] for coord in visited))
    print_grid(grid, visited_coords)
    return len(visited_coords)


def find_highest_scoring_route(grid: Grid) -> int:
    # Returns the minimum valid path cost after the call
    # -1 represents not possible path
    best_known_path = 1_000_000_000_000_000_000

    def explore(
        pos: Coordinate, previousMovement: Movement, path: tuple[int, list[Coordinate]]
    ) -> int:
        nonlocal best_known_path
        pos_contents = grid[pos[1]][pos[0]]
        if pos_contents == "E":
            path[1].append(pos)
            best_known_path = min(path[0], best_known_path)
            return path[0]

        if path[0] > best_known_path:
            return -1

        if pos_contents == "#":
            return -1

        local_path_copy = path[1].copy()

        local_path_copy.append(pos)

        possible_scores: set[int] = set()
        for movement in get_valid_moves(previousMovement):
            next_tile_coord = get_relative_coord(pos, movement)
            next_tile_contents = grid[next_tile_coord[1]][next_tile_coord[0]]

            if next_tile_contents == "#":
                continue

            if next_tile_coord in local_path_copy:
                continue

            if movement == previousMovement:
                score = explore(
                    next_tile_coord, movement, (path[0] + 1, local_path_copy)
                )
                if score != -1:
                    possible_scores.add(score)
            else:
                score = explore(
                    next_tile_coord, movement, (path[0] + 1000 + 1, local_path_copy)
                )
                if score != -1:
                    possible_scores.add(score)

        if len(possible_scores) == 0:
            return -1

        return min(possible_scores)

    initial_player_position = find_char_in_grid("S", grid)
    return explore(initial_player_position, ">", (0, []))


def get_answer(input_file: Path) -> int:
    score = find_highest_scoring_route(parse_input_from_file(input_file))
    return score


def get_answer_dijkstras(input_file: Path) -> int:
    score = dijkstras_algorithm(parse_input_from_file(input_file))
    return score


#assert get_answer(Path(__file__).parent / "test1.txt") == 7036
assert get_answer_dijkstras(Path(__file__).parent / "test1.txt") == 7036
#assert get_answer(Path(__file__).parent / "test2.txt") == 11048
#assert get_answer_dijkstras(Path(__file__).parent / "test2.txt") == 11048
#assert get_answer_dijkstras(Path(__file__).parent / "test7.txt") == 4013
#print(get_answer_dijkstras(Path(__file__).parent / "input.txt"))
