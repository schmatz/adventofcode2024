from pathlib import Path 
from typing import Literal
from dataclasses import dataclass
from collections import Counter
import math
import re

type Coordinate = tuple[int,int]
@dataclass
class RobotData:
    Position: Coordinate
    Velocity: Coordinate

input_text = (Path(__file__).parent / "input.txt").read_text()
GRID_SIZE: Coordinate = (101, 103)

robots: list[RobotData] = []
for line in input_text.splitlines():
    matches = re.search(r"^p=(-?\d+),(-?\d+)\s+v=(-?\d+),(-?\d+)\w*$", line)
    assert(matches is not None and len(matches.groups()) == 4)

    position = (int(matches.group(1)), int(matches.group(2)))
    velocity = (int(matches.group(3)), int(matches.group(4)))

    robot_data = RobotData(position, velocity)
    robots.append(robot_data)

def print_grid(coords: list[Coordinate]):
    for y in range(GRID_SIZE[1]):
        for x in range(GRID_SIZE[0]):
            # count the number of robots at this position
            count = sum(1 for coord in coords if coord == (x, y))
            print(count if count > 0 else ".", end="")
        print()

print_grid([r.Position for r in robots])

def calculate_end_robot_position(robot: RobotData, timesteps: int) -> Coordinate:
    x_pos = (robot.Position[0] + robot.Velocity[0] * timesteps) % GRID_SIZE[0]
    y_pos = (robot.Position[1] + robot.Velocity[1] * timesteps) % GRID_SIZE[1]
    return (x_pos, y_pos)

positions_after_100 = [calculate_end_robot_position(robot, 100) for robot in robots]

print("New positions")
print_grid(positions_after_100)

# 0 represents in the middle, shouldn't count
def get_quadrant(pos: Coordinate, grid_size: Coordinate) -> int:
    middle = (grid_size[0] // 2, grid_size[1] // 2)
    if pos[0] == middle[0] or pos[1] == middle[1]:
        return 0
    
    if pos[0] < middle[0]:
        if pos[1] < middle[1]:
            return 2
        else:
            return 4
    else:
        if pos[1] < middle[1]:
            return 1
        else:
            return 3
    

def calculate_safety_factor(coords: list[Coordinate]):
    counter = Counter([get_quadrant(coord, GRID_SIZE) for coord in coords])

    return math.prod([counter.get(quadrant, 0) for quadrant in range(1, 4 + 1)])

print(calculate_safety_factor(positions_after_100))

def find_christmas_tree():
    i = 0
    while True:
        interesting_one = i * GRID_SIZE[0] + 2
        new_positions = [calculate_end_robot_position(robot, interesting_one) for robot in robots]
        print_grid(new_positions)
        print(f"Timestep: {interesting_one}")
        input()

        interesting_two = i * GRID_SIZE[1] + 76
        new_positions = [calculate_end_robot_position(robot, interesting_two) for robot in robots]
        print_grid(new_positions)
        print(f"Timestep: {interesting_two}")
        input()
        i += 1

find_christmas_tree()

# 2 (vertical), 76 (horizontal), 103 (vertical + 101), 179 (horizontal, +103)