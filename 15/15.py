from pathlib import Path 
from typing import Literal, get_args, cast
from dataclasses import dataclass
from collections import Counter

type Tile = Literal['#', '.', 'O', '@', '[', ']']
type Movement = Literal['^', 'v', '>', '<']
type Coordinate = tuple[int,int]

@dataclass
class ProblemInput:
    grid: list[list[Tile]]
    movements: list[Movement]
    robot_pos: Coordinate

def find_robot_in_grid(grid: list[list[Tile]]) -> Coordinate:
    robot_pos = None
    for y, yline in enumerate(grid):
        for x, xchar in enumerate(yline):
            if xchar == '@':
                robot_pos = (x, y)
                break
        if robot_pos is not None:
            break
    
    if robot_pos is None:
        raise AssertionError("robot needs to be in grid")
    
    return robot_pos

def parse_input_from_file(file: Path) -> ProblemInput:
    input_raw = file.read_text()

    input_lines = [line.strip() for line in input_raw.splitlines()]
    emptyline = input_lines.index('')
    
    grid_lines = input_lines[:emptyline]
    movement_lines = input_lines[emptyline + 1:]

    grid = [list(line) for line in grid_lines]
    movements = list("".join(movement_lines))

    cast_grid = cast(list[list[Tile]], grid)

    return ProblemInput(cast_grid, cast(list[Movement], movements), find_robot_in_grid(cast_grid))
    

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
    


def calculate_gps_sum(problem_input: ProblemInput) -> int:
    s = 0
    for y, yline in enumerate(problem_input.grid):
        for x, xchar in enumerate(yline):
            if xchar == 'O' or xchar == '[':
                s += 100*y + x

    return s

#do_movements(test_input)
#print(calculate_gps_sum(test_input))

# Reset the puzzle

def resize_map(grid: list[list[Tile]]) -> list[list[Tile]]:
    new_grid = []
    for line in grid:
        new_line = []
        for char in line:
            match char:
                case '#':
                    new_line.extend(['#','#'])
                case 'O':
                    new_line.extend(['[',']'])
                case '.':
                    new_line.extend(['.','.'])
                case '@':
                    new_line.extend(['@','.'])
                case _:
                    raise ValueError("Invalid value")
        new_grid.append(new_line)
    return cast(list[list[Tile]], new_grid)

def do_doubled_movements(problem_input: ProblemInput):
    grid = resize_map(problem_input.grid)
    robot_pos = find_robot_in_grid(grid)

    print_grid(grid)


    def can_move(pos: Coordinate, movement: Movement) -> bool:
        next_tile_coord = get_relative_coord(pos, movement)
        next_tile_contents = grid[next_tile_coord[1]][next_tile_coord[0]]
        if next_tile_contents == '#':
            return False
        if next_tile_contents == '.':
            return True
        
        # We need to do the special case to handle vertical movement and double wide boxes
        if movement in ['^', 'v'] and next_tile_contents in ['[', ']']:
            # we need to recurse on both sides of the box
            lateral_movement: Movement = '>' if next_tile_contents == '[' else '<'
            can_move_other_box_side = can_move(get_relative_coord(next_tile_coord, lateral_movement), movement)
            can_move_this_box_side = can_move(next_tile_coord, movement)
            return can_move_this_box_side and can_move_other_box_side
        else:
            return can_move(next_tile_coord, movement)
    
    def do_move(pos: Coordinate, movement: Movement):
        next_tile = get_relative_coord(pos, movement)
        this_tile = grid[pos[1]][pos[0]]

        assert(grid[next_tile[1]][next_tile[0]] != '#')

        # TODO: This is probably a weird corner case
        next_tile_contents = grid[next_tile[1]][next_tile[0]]
        # If we're moving into a free space, bottom out the movement
        if next_tile_contents == '.':
            grid[next_tile[1]][next_tile[0]] = this_tile
            grid[pos[1]][pos[0]] = '.'
            return
        
        if movement in ['^', 'v'] and next_tile_contents in ['[', ']']:
            lateral_movement: Movement = '>' if next_tile_contents == '[' else '<'
            do_move(get_relative_coord(next_tile, lateral_movement), movement)
            do_move(next_tile, movement)
        else:
            do_move(next_tile, movement)
        assert(grid[next_tile[1]][next_tile[0]] == '.')
        grid[next_tile[1]][next_tile[0]] = this_tile
        grid[pos[1]][pos[0]] = '.'
        return
    
    for movement in problem_input.movements:
        if can_move(robot_pos, movement):
            do_move(robot_pos, movement)
            robot_pos = get_relative_coord(robot_pos, movement)
        print("Movement", movement)
        print_grid(grid)
        input()
    test_input.grid = grid
    print(calculate_gps_sum(test_input))

do_doubled_movements(test_input)
