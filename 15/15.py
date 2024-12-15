from pathlib import Path 
from typing import Literal, get_args, cast
from dataclasses import dataclass
from collections import Counter

import math
import re

type Tile = Literal['#', '.', 'O', '@']
type Movement = Literal['^', 'v', '>', '<']
type Coordinate = tuple[int,int]

@dataclass
class ProblemInput:
    grid: list[list[Tile]]
    movements: list[Movement]
    robot_pos: Coordinate


def parse_input_from_file(file: Path) -> ProblemInput:
    input_raw = file.read_text()

    input_lines = [line.strip() for line in input_raw.splitlines()]
    emptyline = input_lines.index('')
    
    grid_lines = input_lines[:emptyline]
    movement_lines = input_lines[emptyline + 1:]

    grid = [list(line) for line in grid_lines]
    movements = list("".join(movement_lines))

    robot_pos = None
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == '@':
                robot_pos = (x, y)
                break
        if robot_pos is not None:
            break

    return ProblemInput(cast(list[list[Tile]], grid), cast(list[Movement], movements), robot_pos)
    

def print_grid(grid: list[list[Tile]]):
    for line in grid:
        print("".join(line))
    
test_input = parse_input_from_file(Path(__file__).parent / "input.txt")


def get_relative_coord(pos: Coordinate, movement: Movement) -> Coordinate:
    match movement:
        case '^':
            return (pos[0], pos[1] - 1)
        case 'v':
            return (pos[0], pos[1] + 1)
        case '<':
            return (pos[0] - 1, pos[1])
        case '>':
            return (pos[0] + 1, pos[1])

def do_movements(problem_input: ProblemInput):
    grid = problem_input.grid
    # Recursively process the movement
    def can_move(pos: Coordinate, movement: Movement) -> bool:
        next_tile = get_relative_coord(pos, movement)
        next_tile_contents = grid[next_tile[1]][next_tile[0]]
        if next_tile_contents == '#':
            return False
        if next_tile_contents == '.':
            return True
        
        return can_move(next_tile, movement)
    
    def do_move(pos: Coordinate, movement: Movement):
        next_tile = get_relative_coord(pos, movement)
        this_tile = grid[pos[1]][pos[0]]
        assert(grid[next_tile[1]][next_tile[0]] != '#')

        if grid[next_tile[1]][next_tile[0]] == '.':
            grid[next_tile[1]][next_tile[0]] = this_tile
            grid[pos[1]][pos[0]] = '.'
            return 

        # Move downstream
        do_move(next_tile, movement)

        assert(grid[next_tile[1]][next_tile[0]] == '.')
        grid[next_tile[1]][next_tile[0]] = this_tile
        grid[pos[1]][pos[0]] = '.'
        return
    
    robot_pos = problem_input.robot_pos
    for movement in problem_input.movements:
        if can_move(robot_pos, movement):
            do_move(robot_pos, movement)
            robot_pos = get_relative_coord(robot_pos, movement)
        #print("Movement", movement)
        #print_grid(grid)
        #input()
    
do_movements(test_input)

def calculate_gps_sum(problem_input: ProblemInput) -> int:
    s = 0
    for y, yline in enumerate(problem_input.grid):
        for x, xchar in enumerate(yline):
            if xchar == 'O':
                s += 100*y + x

    return s

print(calculate_gps_sum(test_input))


        
