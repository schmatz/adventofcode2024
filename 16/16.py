from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush
from collections import defaultdict
import colorama

colorama.init()

type Tile = Literal["#", ".", "S", "E"]
type Coordinate = tuple[int, int]
type Direction = tuple[int, int]
type Grid = list[list[Tile]]

DIRECTIONS: set[Coordinate] = set([(0, 1), (0, -1), (1, 0), (-1, 0)])
INFINITY_VALUE = 1_000_000_000_000_000_000


def find_char_in_grid(char: Tile, grid: Grid) -> Coordinate:
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == char:
                return (x, y)
    assert False, "Tile not found"


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
    (Path(__file__).parent / "output.ans").write_text(output_str)


def get_relative_coord(pos: Coordinate, movement: Direction) -> Coordinate:
    return (pos[0] + movement[0], pos[1] + movement[1])


def reverse_direction(mov: Direction) -> Direction:
    return (mov[0] * -1, mov[1] * -1)


def get_valid_moves(previousMovement: Direction) -> list[Direction]:
    return list(DIRECTIONS - set([reverse_direction(previousMovement)]))


def get_answer_dijkstras(input_file: Path, verbose: bool = False) -> tuple[int, int]:
    grid = parse_input_from_file(input_file)
    dijkstras_distances, dijkstras_previous_nodes = dijkstras_algorithm(grid)

    """
    num_tiles_containing_best_path = int(
        get_num_shortest_path_coordinates_with_neighbors(
            grid, dijkstras_distances, dijkstras_previous_nodes, verbose
        )
    )"""
    num_tiles_containing_best_path = get_num_shortest_path_coordinates_with_distances(
        grid, dijkstras_distances, verbose
    )

    return min(
        [
            dijkstras_distances[(find_char_in_grid("E", grid), direction)]
            for direction in DIRECTIONS
        ]
    ), num_tiles_containing_best_path


def dijkstras_algorithm(
    grid: Grid,
) -> tuple[
    dict[tuple[Coordinate, Direction], int],
    defaultdict[tuple[Coordinate, Direction], set[tuple[Coordinate, Direction]]],
]:
    distances: dict[tuple[Coordinate, Direction], int] = {
        ((x, y), direction): INFINITY_VALUE
        for y, yline in enumerate(grid)
        for x, xchar in enumerate(yline)
        for direction in DIRECTIONS
        if xchar != "#"
    }
    previous_nodes: defaultdict[
        tuple[Coordinate, Direction], set[tuple[Coordinate, Direction]]
    ] = defaultdict(set)

    initial_player_position = find_char_in_grid("S", grid)
    initial_direction = (1, 0)  # east
    distances[(initial_player_position, initial_direction)] = 0
    pq: list[tuple[int, Coordinate, Direction]] = [
        (0, initial_player_position, initial_direction)
    ]
    heapify(pq)

    visited: set[tuple[Coordinate, Direction]] = set()

    # We conceptualize the maze as a 2D maze with 4 dimensions corresponding to the directions.
    # By "turning", we change from one directional dimension to the other.

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


def get_num_shortest_path_coordinates_with_distances(
    grid: Grid,
    distances: dict[tuple[Coordinate, Direction], int],
    verbose: bool = False,
) -> int:
    e_location = find_char_in_grid("E", grid)
    s_location = find_char_in_grid("S", grid)
    shortest_path_dist = min(
        [distances[(e_location, direction)] for direction in DIRECTIONS]
    )
    ending_places = [
        (e_location, direction)
        for direction in DIRECTIONS
        if distances[(e_location, direction)] == shortest_path_dist
    ]

    def explore_backwards(
        pos: Coordinate,
        previousMovement: Direction,
        visited: set[tuple[Coordinate, Direction]],
    ) -> set[tuple[Coordinate, Direction]]:
        visited = visited.copy()
        # Previous movement is forwards
        if (pos, previousMovement) in visited:
            return visited
        visited.add((pos, previousMovement))

        if pos == s_location:
            return visited

        current_distance = distances[(pos, previousMovement)]
        reversed_previous_movement = reverse_direction(previousMovement)

        for movement in get_valid_moves(reversed_previous_movement):
            reversed_movement = reverse_direction(movement)
            if reverse_direction(movement) == previousMovement:
                next_tile_coord = get_relative_coord(pos, reversed_previous_movement)
            else:
                # We haven't moved
                next_tile_coord = pos

            if (next_tile_coord, reversed_movement) not in distances:
                continue

            next_distance = distances[(next_tile_coord, reversed_movement)]

            # We need to check that we actually did arrive from that previous edge,
            # or otherwise the path may be invalid
            movement_cost = 1 if movement == reversed_previous_movement else 1000

            if next_distance + movement_cost == current_distance:
                visited.update(
                    explore_backwards(next_tile_coord, reversed_movement, visited)
                )

        return visited

    total_visited = set()
    # We start by looking at the solu
    for ending_coord, ending_direction in ending_places:
        total_visited.update(explore_backwards(ending_coord, ending_direction, set()))

    visited_coords = {v[0] for v in total_visited}
    if verbose:
        print_grid(grid, visited_coords)
        print("The number of tiles containing best paths is", len(visited_coords))

    return len(visited_coords)


def get_num_shortest_path_coordinates_with_neighbors(
    grid: Grid,
    distances: dict[tuple[Coordinate, Direction], int],
    previous_nodes: defaultdict[
        tuple[Coordinate, Direction], set[tuple[Coordinate, Direction]]
    ],
    verbose: bool = False,
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

    visited: set[tuple[Coordinate, Direction]] = set()

    def explore_backwards(
        pos: Coordinate, previousMovement: Direction, currentCost: int
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

    min_distances: dict[Coordinate, int] = {}
    for distance_tuple, dist in distances.items():
        if distance_tuple[0] not in min_distances:
            min_distances[distance_tuple[0]] = dist
        elif dist < min_distances[distance_tuple[0]]:
            min_distances[distance_tuple[0]] = dist
    visited_coords = {coord[0] for coord in visited}
    if verbose:
        print_grid(grid, visited_coords)
        print_grid_cost(grid, min_distances, visited_coords)
        print("The number of tiles containing best paths is", len(visited_coords))

    return len(visited_coords)


assert get_answer_dijkstras(Path(__file__).parent / "test1.txt", True) == (7036, 45)
assert get_answer_dijkstras(Path(__file__).parent / "test2.txt") == (11048, 64)
input_answers = get_answer_dijkstras(Path(__file__).parent / "input.txt", True)
assert input_answers[0] == 105496
assert input_answers[1] != 582
