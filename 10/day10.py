from pathlib import Path 

input_text = (Path(__file__).parent / "input.txt").read_text()

input_grid = [[int(x if x != '.' else -1) for x in line] for line in input_text.splitlines()]


potential_trailhead_locations = []

for y, yline in enumerate(input_grid):
    for x,location_contents in enumerate(yline):
        if location_contents == 0:
            potential_trailhead_locations.append((x, y))

def get_num_reachable_trailheads(trailhead_loc: tuple[int,int], grid: list[list[int]]) -> int:
    exploration_stack = [trailhead_loc]
    explored_set: set[tuple[int,int]] = set()
    nine_locations: set[tuple[int,int]] = set()

    while len(exploration_stack) > 0:
        current_loc = exploration_stack.pop()
        if current_loc not in explored_set:
            explored_set.add(current_loc)
            
            val = grid[current_loc[1]][current_loc[0]]
            if val == 9:
                nine_locations.add(current_loc)
                continue
            if val == -1:
                continue
            # add left, right, up, down to the stack
            if current_loc[0] > 0:
                coord = (current_loc[0] - 1, current_loc[1])
                if grid[coord[1]][coord[0]] == val + 1:
                    exploration_stack.append(coord)
            if current_loc[0] < len(grid[0]) - 1:
                coord = (current_loc[0] + 1, current_loc[1])
                if grid[coord[1]][coord[0]] == val + 1:
                    exploration_stack.append(coord)
            if current_loc[1] > 0:
                coord = (current_loc[0], current_loc[1] - 1)
                if grid[coord[1]][coord[0]] == val + 1:
                    exploration_stack.append(coord)
            if current_loc[1] < len(grid) - 1:
                coord = (current_loc[0], current_loc[1] + 1)
                if grid[coord[1]][coord[0]] == val + 1:
                    exploration_stack.append(coord)

    return len(nine_locations)

trailhead_sum = sum((get_num_reachable_trailheads(loc, input_grid) for loc in potential_trailhead_locations))
#print(trailhead_sum)

def get_trailhead_rating(trailhead_loc: tuple[int,int], grid: list[list[int]]) -> int:
    unique_paths_to_nines: set[tuple[tuple[int,int], ...]] = set()

    def explore(current_loc: tuple[int, int], path: list[tuple[int,int]]):
        val = grid[current_loc[1]][current_loc[0]]
        if val == 9:
            path.append(current_loc)
            unique_paths_to_nines.add(tuple(path))
            return 
        if val == -1:
            return 
        
        path.append(current_loc)
        if current_loc[0] > 0:
            coord = (current_loc[0] - 1, current_loc[1])
            if grid[coord[1]][coord[0]] == val + 1:
                explore(coord, path)
        if current_loc[0] < len(grid[0]) - 1:
            coord = (current_loc[0] + 1, current_loc[1])
            if grid[coord[1]][coord[0]] == val + 1:
                explore(coord, path)
        if current_loc[1] > 0:
            coord = (current_loc[0], current_loc[1] - 1)
            if grid[coord[1]][coord[0]] == val + 1:
                explore(coord, path)
        if current_loc[1] < len(grid) - 1:
            coord = (current_loc[0], current_loc[1] + 1)
            if grid[coord[1]][coord[0]] == val + 1:
                explore(coord, path)

    explore(trailhead_loc, [])
    return len(unique_paths_to_nines)

rating_sum = sum((get_trailhead_rating(loc, input_grid) for loc in potential_trailhead_locations))
print(rating_sum)