from functools import cache

def calculate_num_stones_after_timestep(input: list[int], timesteps: int) -> list[int]:

    nums = input.copy()
    for timestep in range(timesteps):
        print(timestep, len(nums))
        new_nums = []
        for num in nums:
            string_rep = str(num)
            if num == 0:
                new_nums.append(1)
            elif len(string_rep) % 2 == 0:
                new_nums.extend([int(string_rep[:len(string_rep) // 2]), int(string_rep[len(string_rep) // 2:])])
            else:
                new_nums.append(num * 2024)
        nums = new_nums

    return nums
input = [3935565,31753,437818,7697,5,38,0,123]

print(len(calculate_num_stones_after_timestep(input, 25)))

@cache
def calculate_num_stones_recursive(num: int, timestep: int) -> int:
    if timestep == 0:
        return 1
    if num == 0:
        return calculate_num_stones_recursive(1, timestep - 1)
    elif len(str(num)) % 2 == 0:
        string_rep = str(num)
        return calculate_num_stones_recursive(int(string_rep[:len(string_rep) // 2]), timestep - 1) + calculate_num_stones_recursive(int(string_rep[len(string_rep) // 2:]), timestep - 1)
    else:
        return calculate_num_stones_recursive(num  * 2024, timestep - 1)


print(sum([calculate_num_stones_recursive(num, 75) for num in input]))
