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

def simple_dijkstras_algorithm(grid: Grid) -> dict[Coordinate, int]:
    distances: dict[Coordinate, int] = {}

    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == '#':
                continue
            else:
                distances[(x,y)] = INFINITY_VALUE

    start_coord = find_char_in_grid('S', grid)

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

    return distances


#print(simple_dijkstras_algorithm(input_grid))

input_grid = parse_input_from_file("input.txt")

original_dijkstras_distances = simple_dijkstras_algorithm(input_grid)

end_coord = find_char_in_grid('E', input_grid)
original_distance_to_end = original_dijkstras_distances[end_coord]


# Rather than reprocessing the Dijkstra's, just explore all reachable positions with N turns and then resume the algorithm

BASE_DIRECTIONS = base_directions = [(0,1), (0,-1), (1, 0), (-1, 0)]

def get_end_pos(start: Coordinate, moves: tuple[Coordinate, ...]) -> Coordinate:
    x = start[0]
    y = start[1]
    for combo in moves:
        x += combo[0]
        y += combo[1]
    
    return (x,y)

MAX_CHEAT_DISTANCE = 20
cheat_completion_times: dict[tuple[Coordinate, Coordinate], int] = {}
# TODO: Need to account for early reaching of goal
for y, yline in enumerate(input_grid):
    print("Processing line", y)
    for x, xchar in enumerate(yline):
        if xchar == '#':
            continue
        start_coord = (x,y)
        original_cost = original_distance_to_end - original_dijkstras_distances[start_coord]
        for finish_coord in original_dijkstras_distances.keys():
            manhattan_distance = abs(start_coord[0] - finish_coord[0]) + abs(start_coord[1] - finish_coord[1])
            
            if manhattan_distance > MAX_CHEAT_DISTANCE:
                continue

            if start_coord == finish_coord:
                continue

            finish_char = input_grid[finish_coord[1]][finish_coord[0]]
            assert finish_char != '#'

            new_cost = original_distance_to_end - original_dijkstras_distances[finish_coord] + manhattan_distance
            # We now incur a movement of cheat_distance
            time_savings = original_cost - new_cost
            if time_savings <= 0:
                continue # We don't save any time by doing the cheat
            
            cheat_completion_times[(start_coord, finish_coord)] = time_savings
            


grouped_savings = Counter(cheat_completion_times.values())
del grouped_savings[0]
print(sorted(grouped_savings.items()))
print(sum([num_cheats for amount_savings, num_cheats in grouped_savings.items() if amount_savings >= 100]))
