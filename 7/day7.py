from pathlib import Path

input_text = (Path(__file__).parent / "input.txt").read_text()

problems = []

for line in input_text.splitlines():
    colon_split = line.split(":")
    assert len(colon_split) == 2
    answer = int(colon_split[0])
    components = [int(num) for num in colon_split[1].split()]

    problems.append((answer, components))


def get_sum(target: int, lhs: int, components: list[int]) -> int:
    if len(components) == 0:
        return lhs if lhs == target else 0
    components_copy = components[:]
    next_elem = components_copy.pop(0)

    if mult_answer := get_sum(target, lhs * next_elem, components_copy):
        return mult_answer
    if add_answer := get_sum(target, lhs + next_elem, components_copy):
        return add_answer
    if concat_answer := get_sum(
        target, int(str(lhs) + str(next_elem)), components_copy
    ):
        return concat_answer

    return False


valid_sum = 0
for answer, components in problems:
    original_components = components[:]
    first_component = components.pop(0)
    if test_value := get_sum(answer, first_component, components):
        valid_sum += test_value

print(valid_sum)
