from pathlib import Path

input_text = (Path(__file__).parent / "input.txt").read_text()

dense_disk_map = [int(char) for char in input_text]

FREE_SPACE_MARKER = -1

expanded_disk_map = []
unfragmented_disk_map = []
current_id = 0
for i, num in enumerate(dense_disk_map):
    if num == 0:
        continue
    is_file_marker = i % 2 == 0
    if is_file_marker:
        # Can't do this because IDs won't be preserved
        unfragmented_disk_map.append((current_id, num))
        expanded_disk_map.extend([current_id] * num)
        current_id += 1
    else:
        # It's free space
        unfragmented_disk_map.append((FREE_SPACE_MARKER, num))
        expanded_disk_map.extend([FREE_SPACE_MARKER] * num)

rightmost_file_index = len(expanded_disk_map) - 1
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] != FREE_SPACE_MARKER:
        continue

    if expanded_disk_map[rightmost_file_index] == FREE_SPACE_MARKER:
        for j in reversed(range(i + 1, rightmost_file_index + 1)):
            if expanded_disk_map[j] != FREE_SPACE_MARKER:
                rightmost_file_index = j
                break
        else:
            break

    expanded_disk_map[i], expanded_disk_map[rightmost_file_index] = (
        expanded_disk_map[rightmost_file_index],
        expanded_disk_map[i],
    )

checksum = 0
for i in range(len(expanded_disk_map)):
    if expanded_disk_map[i] == FREE_SPACE_MARKER:
        continue
    checksum += i * int(expanded_disk_map[i])
print(checksum)

defragged_ids: set[int] = set()


def unfragment_one_file(
    disk_map: list[tuple[int, int]], defragmented_file_ids: set[int]
) -> bool:
    # Now do a defragmentation of the unfragmented disk map
    for i in reversed(range(len(disk_map))):
        fragment = disk_map[i]
        fragment_id = fragment[0]
        fragment_size = fragment[1]
        if fragment_id == FREE_SPACE_MARKER or fragment_id in defragmented_file_ids:
            continue

        for j in range(i):
            free_space_fragment = disk_map[j]
            free_space_fragment_id = free_space_fragment[0]
            free_space_fragment_size = free_space_fragment[1]
            if (
                free_space_fragment_id != FREE_SPACE_MARKER
                or free_space_fragment_size < fragment_size
            ):
                continue

            disk_map[i], disk_map[j] = (FREE_SPACE_MARKER, fragment_size), fragment
            size_differential = free_space_fragment_size - fragment_size
            if size_differential > 0:
                disk_map.insert(j + 1, (FREE_SPACE_MARKER, size_differential))
            defragmented_file_ids.add(fragment_id)
            return False

    return True


# Jank but whatever
while True:
    done = unfragment_one_file(unfragmented_disk_map, defragged_ids)
    if done:
        print("Done defragmenting!")
        break

final_disk_map = []

current_free_space_span = (FREE_SPACE_MARKER, 0)
for elem in unfragmented_disk_map:
    if elem[0] != FREE_SPACE_MARKER:
        if current_free_space_span[1] > 0:
            final_disk_map.append(current_free_space_span)
            current_free_space_span = (FREE_SPACE_MARKER, 0)
        final_disk_map.append(elem)
    else:
        current_free_space_span = (
            FREE_SPACE_MARKER,
            current_free_space_span[1] + elem[1],
        )

if current_free_space_span[1] != 0:
    final_disk_map.append(current_free_space_span)


checksum = 0
current_index = 0
for i in range(len(final_disk_map)):
    block_id = final_disk_map[i][0]
    block_size = final_disk_map[i][1]
    if block_id == FREE_SPACE_MARKER:
        current_index += block_size
        continue
    for j in range(block_size):
        checksum += (current_index + j) * block_id
    current_index += block_size
print(checksum)
