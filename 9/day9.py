from pathlib import Path 

input_text = (Path(__file__).parent / "input.txt").read_text()

dense_disk_map = [int(char) for char in input_text]

FREE_SPACE_MARKER = -1

expanded_disk_map = []
current_id = 0
for i, num in enumerate(dense_disk_map):
    if num == 0:
        continue
    is_file_marker = i % 2 == 0
    if is_file_marker:
        # Can't do this because IDs won't be preserved
        expanded_disk_map.extend([current_id] * num)
        current_id += 1
    else:
        # It's free space
        expanded_disk_map.extend([FREE_SPACE_MARKER] * num)

rightmost_file_index = len(expanded_disk_map) - 1
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] != FREE_SPACE_MARKER:
        continue

    if expanded_disk_map[rightmost_file_index] == FREE_SPACE_MARKER:
        for j in reversed(range(i+1, rightmost_file_index + 1)):
            if expanded_disk_map[j] != FREE_SPACE_MARKER:
                rightmost_file_index = j
                break
        else:
            break
    
    expanded_disk_map[i], expanded_disk_map[rightmost_file_index] = expanded_disk_map[rightmost_file_index], expanded_disk_map[i]

checksum = 0
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] == FREE_SPACE_MARKER:
        continue
    checksum += i * int(expanded_disk_map[i])
print(checksum)
    
