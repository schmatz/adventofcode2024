from pathlib import Path 

input_text = (Path(__file__).parent / "test1.txt").read_text()

dense_disk_map = [int(char) for char in input_text]

expanded_disk_map = []
current_id = 0
for i, num in enumerate(dense_disk_map):
    if num == 0:
        continue
    is_file_marker = i % 2 == 0
    if is_file_marker:
        # Can't do this because IDs won't be preserved
        expanded_disk_map.extend([str(current_id)] * num)
        current_id += 1
    else:
        # It's free space
        expanded_disk_map.extend(['.'] * num)

print(expanded_disk_map)

rightmost_file_index = len(expanded_disk_map) - 1
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] != ".":
        continue

    if expanded_disk_map[rightmost_file_index] == '.':
        for j in reversed(range(i+1, rightmost_file_index + 1)):
            if expanded_disk_map[j] != '.':
                rightmost_file_index = j
                break
        else:
            print("Ran out of files to compact")
            break
    
    expanded_disk_map[i], expanded_disk_map[rightmost_file_index] = expanded_disk_map[rightmost_file_index], expanded_disk_map[i]

print(expanded_disk_map)

checksum = 0
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] == '.':
        continue
    checksum += i * int(expanded_disk_map[i])
print(checksum)
    
