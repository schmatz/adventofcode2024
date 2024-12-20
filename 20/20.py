from pathlib import Path
from typing import Literal, cast
from heapq import heapify, heappop, heappush
from collections import Counter

type Tile = Literal["#", ".", "S", "E"]
type Coordinate = tuple[int, int]
type Movement = Literal["^", "v", ">", "<"]

type Grid = list[list[Tile]]


def parse_input_from_file(filename: str) -> Grid:
    input_raw = (Path(__file__).parent / filename).read_text()
    input_lines = [line.strip() for line in input_raw.splitlines()]

    grid = [list(line) for line in input_lines]

    return cast(Grid, grid)

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

    start_coord = find_char_in_grid('S', grid)
    end_coord = find_char_in_grid('E', grid)

    distances[start_coord] = 0
    pq: list[tuple[int, Coordinate]] = [(0, start_coord)]
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

    return distances[end_coord]


#print(simple_dijkstras_algorithm(input_grid))

input_grid = parse_input_from_file("input.txt")

original_completion_time = simple_dijkstras_algorithm(input_grid)

cheat_completion_times: dict[Coordinate, int] = {}
# Remove each wall and recalculate
for y, yline in enumerate(input_grid):
    print("processing", y, "yline")
    for x, xchar in enumerate(yline):
        if xchar == '#':
            old_val = input_grid[y][x]
            input_grid[y][x] = '.'
            completion_time = simple_dijkstras_algorithm(input_grid)
            cheat_completion_times[(x,y)] = completion_time
            #if y == 7 and x == 6:
            #    print("Cheating completion time", completion_time, "saves", original_completion_time - completion_time)
            input_grid[y][x] = old_val

grouped_savings = Counter([original_completion_time - completion_time for completion_time in cheat_completion_times.values()])
del grouped_savings[0]
print(sorted(grouped_savings.items()))
print(sum([y for x, y in grouped_savings.items() if x >= 100]))