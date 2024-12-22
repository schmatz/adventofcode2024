from pathlib import Path
from typing import Literal

input_text = (Path(__file__).parent / "input.txt").read_text()

input_grid = [list(line) for line in input_text.splitlines()]

type Direction = Literal["N", "E", "S", "W"]
type Coordinate = tuple[int, int]

directions: list[Direction] = ["N", "E", "S", "W"]


def get_relative_coord(coord: Coordinate, direction: Direction) -> Coordinate:
    match direction:
        case "E":
            return (coord[0] + 1, coord[1])
        case "N":
            return (coord[0], coord[1] - 1)
        case "S":
            return (coord[0], coord[1] + 1)
        case "W":
            return (coord[0] - 1, coord[1])


def get_perpendicular_directions(direction: Direction) -> tuple[Direction, Direction]:
    match direction:
        case "E" | "W":
            return ("N", "S")
        case "N" | "S":
            return ("E", "W")


# Let's do some flood filling
# Flood fill all connected elements and then change the elements to use a marker


def get_region_elements(
    original_pos: Coordinate, grid: list[list[str]]
) -> set[Coordinate]:
    region_coordinates: set[Coordinate] = set()
    original_region = grid[original_pos[1]][original_pos[0]]

    def explore(pos: Coordinate):
        if pos in region_coordinates:
            return

        r = grid[pos[1]][pos[0]]
        if r != original_region:
            return

        region_coordinates.add(pos)

        for direction in directions:
            new_coord = get_relative_coord(pos, direction)
            if (
                new_coord[0] >= 0
                and new_coord[0] < len(grid)
                and new_coord[1] >= 0
                and new_coord[1] < len(grid[0])
            ):
                explore(new_coord)

    explore(original_pos)
    return region_coordinates


def get_region_coordinates_for_grid(
    input_grid: list[list[str]],
) -> set[frozenset[Coordinate]]:
    explored_positions: set[Coordinate] = set()
    region_coordinates: set[frozenset[Coordinate]] = set()
    for y in range(len(input_grid)):
        for x in range(len(input_grid[y])):
            if (x, y) in explored_positions:
                continue
            coords = get_region_elements((x, y), input_grid)
            explored_positions.update(coords)
            region_coordinates.add(frozenset(coords))
    return region_coordinates


region_coordinates = get_region_coordinates_for_grid(input_grid)


def calculate_perimeter(positions: set[Coordinate]) -> int:
    calculated_coords: set[Coordinate] = set()

    def explore(pos: Coordinate) -> int:
        if pos in calculated_coords:
            return 0
        if pos not in positions:
            return 1

        calculated_coords.add(pos)
        return sum(
            [explore(get_relative_coord(pos, direction)) for direction in directions]
        )

    return explore(next(iter(positions)))


price_sum = sum(
    [(len(coords) * calculate_perimeter(set(coords))) for coords in region_coordinates]
)
print(price_sum)


# Equivalent to counting corners
def calculate_num_sides(positions: set[Coordinate], input_grid: list[list[str]]) -> int:
    explored_coordinates: set[Coordinate] = set()

    def explore(position: Coordinate) -> int:
        corners = 0

        explored_coordinates.add(position)
        for direction_one, direction_two in zip(
            directions, [*directions[1:], directions[0]]
        ):
            relative_coord_one = get_relative_coord(position, direction_one)
            relative_coord_two = get_relative_coord(position, direction_two)
            # If there isn't an edge in the direction, continue
            if (
                relative_coord_one not in positions
                and relative_coord_two not in positions
            ):
                corners += 1

            # Look for the other type of corner
            corner_pos = (
                relative_coord_one[0]
                if relative_coord_one[0] != position[0]
                else relative_coord_two[0],
                relative_coord_one[1]
                if relative_coord_one[1] != position[1]
                else relative_coord_two[1],
            )

            if (
                relative_coord_one in positions
                and relative_coord_two in positions
                and corner_pos not in positions
            ):
                corners += 1

        for direction in directions:
            new_coord = get_relative_coord(position, direction)
            if new_coord not in explored_coordinates and new_coord in positions:
                corners += explore(new_coord)

        return corners

    return explore(next(iter(positions)))


def get_cost_for_file(filename: str) -> int:
    input_text = (Path(__file__).parent / filename).read_text()

    input_grid = [list(line) for line in input_text.splitlines()]
    region_coordinates = get_region_coordinates_for_grid(input_grid)
    price_sum = 0
    for coords in region_coordinates:
        area = len(coords)
        num_sides = calculate_num_sides(set(coords), input_grid)
        price_sum += area * num_sides

    return price_sum


assert get_cost_for_file("test1.txt") == 80
assert get_cost_for_file("test4.txt") == 236
assert get_cost_for_file("test5.txt") == 368
assert get_cost_for_file("test2.txt") == 436
assert get_cost_for_file("test3.txt") == 1206

print(get_cost_for_file("input.txt"))
