from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush

type Tile = Literal["#", ".", "S", "E"]
type Coordinate = tuple[int, int]
type Movement = Literal["^", "v", ">", "<"]

type Grid = list[list[Tile]]


def parse_input_from_file(filename: str) -> list[Coordinate]:
    input_raw = (Path(__file__).parent / filename).read_text()

    input_lines = [line.split(",") for line in input_raw.splitlines()]

    return [(int(line[0]), int(line[1])) for line in input_lines]

def simulate_grid_after_timesteps(coords: list[Coordinate], timesteps: int, grid_size: int) -> Grid:
    grid = [['.' for x in range(grid_size)] for y in range(grid_size)]

    for coord in coords[:timesteps]:
        grid[coord[1]][coord[0]] = '#'

    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            print(xchar, end='')
        print()

    cast_grid = cast(Grid, grid)
    return cast_grid
    

input_coords = parse_input_from_file("test1.txt")

input_grid = simulate_grid_after_timesteps(input_coords, 12, 7)

INFINITY_VALUE = 1_000_000_000_000_000_000

DIRECTIONS = [(0,1), (0, -1), (1, 0), (-1, 0)]

def simple_dijkstras_algorithm(grid: Grid) -> int:
    distances: dict[Coordinate, int] = {}

    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == '#':
                continue
            else:
                distances[(x,y)] = INFINITY_VALUE

    distances[(0,0)] = 0
    pq: list[tuple[int, Coordinate]] = [(0, (0,0))]
    heapify(pq)

    visited: set[Coordinate] = set()

    while pq:
        current_distance, pos = heappop(pq)
        if pos in visited:
            continue

        visited.add(pos)

        for direction in DIRECTIONS:
            next_coord = (pos[0] + direction[0], pos[1] + direction[1])

            if next_coord not in distances:
                continue

            tentative_distance = current_distance + 1

            if tentative_distance < distances[next_coord]:
                distances[next_coord] = tentative_distance
                heappush(pq, (tentative_distance, next_coord))

    return distances[(len(grid) - 1, len(grid[0]) -1)]


#print(simple_dijkstras_algorithm(input_grid))


input_coords = parse_input_from_file("input.txt")

for i in range(0, len(input_coords)):
    input_grid = simulate_grid_after_timesteps(input_coords, i, 71)
    minimum_steps =simple_dijkstras_algorithm(input_grid)
    if minimum_steps == INFINITY_VALUE:
        print(f"No path at step {i}, {input_coords[i -1]}")
        break