from pathlib import Path 
import copy

input_txt = (Path(__file__).parent / "input.txt").read_text()

grid: list[list[str]] = [list(line) for line in input_txt.splitlines()]

guard_pos = None
for y, y_line in enumerate(grid):
    if '^' in y_line:
        guard_pos = (y_line.index('^'), y)
        grid[guard_pos[1]][guard_pos[0]] = '.'

assert guard_pos is not None

print(guard_pos)
# Loop
def walk_guard(guard_pos: tuple[int, int], grid: list[list[str]]) -> tuple[int, bool]:
    guard_on_map = True 
    guard_direction = '^'
    visited_positions = set()
    visited_positions.add(guard_pos)

    loop_positions = set()
    loop_positions.add((guard_pos, guard_direction))
    
    while guard_on_map:
        #print(guard_pos)
        new_guard_x = guard_pos[0]
        new_guard_y = guard_pos[1]
        match guard_direction:
            case '^':
                new_guard_y -= 1
            case '>':
                new_guard_x += 1
            case 'v':
                new_guard_y += 1
            case '<':
                new_guard_x -= 1

        if new_guard_y < 0 or new_guard_y == len(grid):
            break
        if new_guard_x < 0 or new_guard_x == len(grid[0]):
            break

        new_square = grid[new_guard_y][new_guard_x]
        if new_square == '#':
            match guard_direction:
                case '^':
                    guard_direction = '>'
                case '>':
                    guard_direction = 'v'
                case 'v':
                    guard_direction = '<'
                case '<':
                    guard_direction = '^'
            # Go to the next loop iteration
            #print("Changing direction to ", guard_direction)
            continue
        
        guard_pos = (new_guard_x, new_guard_y)
        if (guard_pos, guard_direction) in loop_positions:
            return len(visited_positions), True
    
        visited_positions.add(guard_pos)
        loop_positions.add((guard_pos, guard_direction))
    return len(visited_positions), False

print(walk_guard(guard_pos, grid))


num_loops = 0
for x in range(len(grid[0])):
    print(x, len(grid[0]))
    for y in range(len(grid)):
        if (x,y) == guard_pos or grid[y][x] == "#":
            continue
        grid[y][x] = '#'
        _, loop = walk_guard(guard_pos, grid)
        if loop:
            num_loops += 1
        grid[y][x] = '.'

print("Num loops", num_loops)




