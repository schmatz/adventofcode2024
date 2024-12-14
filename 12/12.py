from pathlib import Path 
from typing import Literal

input_text = (Path(__file__).parent / "test3.txt").read_text()

input_grid = [list(line) for line in input_text.splitlines()]

# Let's do some flood filling
# Flood fill all connected elements and then change the elements to use a marker

def get_region_elements(original_pos: tuple[int,int], grid: list[list[str]]) -> set[tuple[int,int]]:
    region_coordinates: set[tuple[int,int]] = set()
    original_region = grid[original_pos[1]][original_pos[0]]
    def explore(pos: tuple[int,int]):
        if pos in region_coordinates:
            return
        
        r = grid[pos[1]][pos[0]]
        if r != original_region:
            return
        
        region_coordinates.add(pos)
        
        if pos[1] - 1 >= 0:
            explore((pos[0], pos[1] - 1))
        if pos[1] + 1 < len(grid):
            explore((pos[0], pos[1] + 1))
        if pos[0] - 1 >= 0:
            explore((pos[0] - 1, pos[1]))
        if pos[0] + 1 < len(grid[0]):
            explore((pos[0] + 1, pos[1]))

    explore(original_pos)
    return region_coordinates

explored_positions: set[tuple[int,int]] = set()
region_coordinates: set[frozenset[tuple[int,int]]] = set()
for y in range(len(input_grid)):
    for x in range(len(input_grid[y])):
        if (x,y) in explored_positions:
            continue
        coords = get_region_elements((x,y), input_grid)
        explored_positions.update(coords)
        region_coordinates.add(frozenset(coords))
   

def calculate_perimeter(positions: set[tuple[int,int]]) -> int:
    calculated_coords: set[tuple[int,int]] = set()

    def explore(pos: tuple[int,int]) -> int:
        if pos in calculated_coords:
            return 0
        if pos not in positions:
            return 1
        
        calculated_coords.add(pos)
        return explore((pos[0] - 1, pos[1])) + explore((pos[0] + 1, pos[1])) + explore((pos[0], pos[1] - 1)) + explore((pos[0], pos[1] + 1))

    return explore(next(iter(positions)))

def get_next_coord(pos: tuple[int,int], dir: Literal['N','S','E','W']):
    match dir:
        case 'E':
            # south
            return pos + (0,1)
        case 'W':
            # north 
            return pos + (0, -1)
        case 'N':
            # east
            return pos + (1, 0)
        case 'S':
            # west
            return pos + (-1, 0)
            

price_sum = 0
for coords in region_coordinates:
    example_coord = next(iter(coords))
    area = len(coords)
    perimeter = calculate_perimeter(coords)
    #print(f"{input_grid[example_coord[1]][example_coord[0]]} has area {area} and perimeter {perimeter}, for price {area * perimeter}")
    price_sum += area * perimeter


type Direction = Literal['N','S','E','W']
type Coordinate = tuple[int,int]

def calculate_num_sides(positions: set[Coordinate]) -> int:
    explored_coordinates: set[Coordinate] = set()
    directions = set(['N','S','E','W'])

    coords_to_edges: dict[Coordinate, set[Direction]] = {}

    def explore(position: tuple[int,int], previous_sides: set[Direction]) -> int:
        if position in explored_coordinates:
            return 0
        explored_coordinates.add(position)
    
        new_sides = 0
        existing_edge_directions: set[Direction] = set()
        coordinates_to_recurse: set[Coordinate] = set()
        
        for direction in directions:
            if direction == 'E':
                new_coord = (position[0] + 1, position[1])
                if new_coord not in positions:
                    if 'E' not in previous_sides:
                        north_directions = coords_to_edges.get((position[0], position[1] - 1), set())
                        south_directions = coords_to_edges.get((position[0], position[1] + 1), set())
                        if 'E' not in north_directions and 'E' not in south_directions:
                            new_sides += 1
                    existing_edge_directions.add('E')
                else:
                    coordinates_to_recurse.add(new_coord)
            elif direction == 'N':
                new_coord = (position[0], position[1] -1)
                if new_coord not in positions:
                    if 'N' not in previous_sides:
                        east_directions = coords_to_edges.get((position[0] + 1, position[1]), set())
                        west_directions = coords_to_edges.get((position[0] - 1, position[1]), set())
                        if 'N' not in east_directions and 'N' not in west_directions:
                            new_sides += 1
                    existing_edge_directions.add('N')
                else:
                    coordinates_to_recurse.add(new_coord)
            elif direction == 'S':
                new_coord = (position[0], position[1] +1)
                if new_coord not in positions:
                    if 'S' not in previous_sides:
                        east_directions = coords_to_edges.get((position[0] + 1, position[1]), set())
                        west_directions = coords_to_edges.get((position[0] - 1, position[1]), set())
                        if 'S' not in east_directions and 'S' not in west_directions:
                            new_sides += 1
                    existing_edge_directions.add('S')
                else:
                    coordinates_to_recurse.add(new_coord)
            elif direction == 'W':
                new_coord = (position[0] - 1, position[1])
                if new_coord not in positions:
                    if 'W' not in previous_sides:
                        # check if north and south don't have this coord
                        north_directions = coords_to_edges.get((position[0], position[1] - 1), set())
                        south_directions = coords_to_edges.get((position[0], position[1] + 1), set())
                        if 'W' not in north_directions and 'W' not in south_directions:
                            new_sides += 1
                    existing_edge_directions.add('W')
                else:
                    coordinates_to_recurse.add(new_coord)

        coords_to_edges[position] = existing_edge_directions

            # recurse laterally to directions not present in continue
        for coord in coordinates_to_recurse:
            new_sides += explore(coord, existing_edge_directions)
        return new_sides
                
                
    return explore(next(iter(positions)), set())

price_sum = 0
for coords in region_coordinates:
    example_coord = next(iter(coords))
    area = len(coords)
    if input_grid[example_coord[1]][example_coord[0]] == 'B':
        print("looking at B now")
    num_sides = calculate_num_sides(coords)

    print(f"{input_grid[example_coord[1]][example_coord[0]]} has area {area} and num_sides {num_sides}, for price {area * num_sides}")
    price_sum += area * num_sides

print(price_sum)