from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush
from collections import defaultdict
import colorama

colorama.init()

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
                output_str += f"{colorama.Fore.RED}O{colorama.Style.RESET_ALL}"
            else:
                output_str += xchar
        output_str += "\n"
    print(output_str)


def print_grid_cost(
    grid: list[list[Tile]], distances: dict[Coordinate, int], coords: set[Coordinate]
):
    output_str = ""
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if (x, y) in distances:
                if (x, y) in coords:
                    output_str += f"{colorama.Fore.RED}{distances[(x,y)]:06}{colorama.Style.RESET_ALL} "
                else:
                    output_str += f"{distances[(x,y)]:06} "
            else:
                output_str += xchar * 6 + " "
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
            return "<"
        case "^":
            return "v"
        case "<":
            return ">"
        case "v":
            return "^"


INFINITY_VALUE = 1_000_000_000_000_000_000
DIRECTIONS: set[Movement] = {"^", ">", "v", "<"}


# Do Dijkstra's algorith, return the distances
def dijkstras_algorithm(
    grid: Grid,
) -> tuple[
    dict[tuple[Coordinate, Movement], int],
    defaultdict[tuple[Coordinate, Movement], set[tuple[Coordinate, Movement]]],
]:
    distances: dict[tuple[Coordinate, Movement], int] = {}
    previous_nodes: defaultdict[
        tuple[Coordinate, Movement], set[tuple[Coordinate, Movement]]
    ] = defaultdict(set)

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

            if tentative_distance <= distances[(next_tile_coord, movement)]:
                distances[(next_tile_coord, movement)] = tentative_distance
                previous_nodes[(next_tile_coord, movement)].add((pos, previousMovement))
                heappush(pq, (tentative_distance, next_tile_coord, movement))

    return distances, previous_nodes


def get_num_shortest_path_coordinates_with_neighbors(
    grid: Grid,
    distances: dict[tuple[Coordinate, Movement], int],
    previous_nodes: defaultdict[
        tuple[Coordinate, Movement], set[tuple[Coordinate, Movement]]
    ],
) -> int:
    e_location = find_char_in_grid("E", grid)
    shortest_path_dist = min(
        [distances[(e_location, direction)] for direction in DIRECTIONS]
    )
    starting_directions = [
        (e_location, direction)
        for direction in DIRECTIONS
        if distances[(e_location, direction)] == shortest_path_dist
    ]

    visited: set[tuple[Coordinate, Movement]] = set()

    def explore_backwards(
        pos: Coordinate, previousMovement: Movement, currentCost: int
    ):
        if (pos, previousMovement) in visited:
            return
        visited.add((pos, previousMovement))

        for coord, movement in previous_nodes[(pos, previousMovement)]:
            explore_backwards(coord, movement, distances[(coord, movement)])

    assert len(starting_directions) == 1
    for direction in starting_directions:
        explore_backwards(
            direction[0], direction[1], distances[(direction[0], direction[1])]
        )

    visited_coords = set(coord[0] for coord in visited)
    print_grid(grid, visited_coords)

    min_distances: dict[Coordinate, int] = {}
    for distance_tuple, dist in distances.items():
        if distance_tuple[0] not in min_distances:
            min_distances[distance_tuple[0]] = dist
        elif dist < min_distances[distance_tuple[0]]:
            min_distances[distance_tuple[0]] = dist

    print_grid_cost(grid, min_distances, visited_coords)

    return len(visited_coords)


def get_answer_dijkstras(input_file: Path) -> int:
    grid = parse_input_from_file(input_file)
    dijkstras_distances, dijkstras_previous_nodes = dijkstras_algorithm(grid)

    num_tiles_containing_best_path = int(
        get_num_shortest_path_coordinates_with_neighbors(
            grid, dijkstras_distances, dijkstras_previous_nodes
        )
    )
    print(
        "The number of tiles containing best paths is", num_tiles_containing_best_path
    )

    return min(
        [
            dijkstras_distances[(find_char_in_grid("E", grid), direction)]
            for direction in DIRECTIONS
        ]
    )


assert get_answer_dijkstras(Path(__file__).parent / "test1.txt") == 7036
assert get_answer_dijkstras(Path(__file__).parent / "test2.txt") == 11048
# print(
#    "The answer to part 1 is", get_answer_dijkstras(Path(__file__).parent / "input.txt")
# )
