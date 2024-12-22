from pathlib import Path


input_text = (Path(__file__).parent / "input.txt").read_text()

rules = []
updates = []

for line in input_text.splitlines():
    if line.strip() == "":
        continue
    if "|" in line:
        split = line.split("|")
        assert len(split) == 2
        rule = (split[0], split[1])
        rules.append(rule)
    if "," in line:
        update = line.split(",")
        assert len(update) % 2 == 1
        updates.append(update)


def update_is_valid(update: list[str], rules: list[tuple[str, str]]) -> bool:
    for rule in rules:
        before = rule[0]
        after = rule[1]

        if before not in update or after not in update:
            continue

        if update.index(before) > update.index(after):
            return False

    return True


def get_middle_number(update: list[str]) -> int:
    return int(update[len(update) // 2])


valid_updates = [update for update in updates if update_is_valid(update, rules)]


print(sum([get_middle_number(update) for update in valid_updates]))

invalid_updates = [update for update in updates if not update_is_valid(update, rules)]


def reorder_update(update: list[str], rules: list[tuple[str, str]]) -> list[str]:
    for rule in rules:
        before = rule[0]
        after = rule[1]

        if before not in update or after not in update:
            continue

        if update.index(before) > update.index(after):
            update[update.index(before)], update[update.index(after)] = (
                update[update.index(after)],
                update[update.index(before)],
            )

    return update


reordered_updates = []
for invalid_update in invalid_updates:
    while not update_is_valid(invalid_update, rules):
        reorder_update(invalid_update, rules)
    reordered_updates.append(invalid_update)


print(sum([get_middle_number(update) for update in reordered_updates]))
