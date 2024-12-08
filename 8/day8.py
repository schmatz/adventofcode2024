from pathlib import Path 
from collections import defaultdict
import itertools

input_text = (Path(__file__).parent / "input.txt").read_text()

grid: list[list[str]] = [list(line.strip()) for line in input_text.splitlines()]

grid_size = (len(grid[0]),len(grid))
grid_locations: dict[str, list[tuple[int,int]]] = defaultdict(list)
for y in range(grid_size[1]):
    for x in range(grid_size[0]):
        char = grid[y][x]
        if char != '.':
            grid_locations[char].append((x,y))

print(grid_size)

def get_antinode_locations(locations: list[tuple[int,int]], grid_size: tuple[int,int]) -> set[tuple[int,int]]:
    antinode_locations = set()
    for node_one, node_two in itertools.permutations(locations, 2):
        x_difference = node_two[0] - node_one[0]
        y_difference = node_two[1] - node_one[1]

        i = 0.0
        while True:
            new_location = (i * x_difference + node_one[0], i * y_difference + node_one[1])
            assert new_location[0].is_integer()
            assert new_location[1].is_integer()
            new_location = (int(new_location[0]), int(new_location[1]))
            if new_location[0] >= grid_size[0] or new_location[0] < 0 or new_location[1] >= grid_size[1] or new_location[1] < 0:
                break
            antinode_locations.add(new_location)
            i += 1

        
    return antinode_locations

antinode_locations_by_antenna = [get_antinode_locations(grid_locations[antenna], grid_size) for antenna in grid_locations.keys()]

antinode_locations: set[tuple[int,int]] = set()
antinode_locations.update(*antinode_locations_by_antenna)

print(len(antinode_locations))

