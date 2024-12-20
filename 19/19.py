from pathlib import Path
from dataclasses import dataclass
from functools import cache

@dataclass 
class TrieNode:
    text: str | None
    children: dict[str, "TrieNode"]
    is_word: bool = False

    def __eq__(self, other):
        return (self == other)

    def __hash__(self):
        return id(self)

def build_trie(towels: set[str]) -> TrieNode:
    root = TrieNode(None, {})

    for towel in towels:
        current = root 
        for i, char in enumerate(towel):
            if char not in current.children:
                prefix = towel[:i+1]
                current.children[char] = TrieNode(prefix, {})
            current = current.children[char]
        current.is_word = True
    return root

def find_trie(root: TrieNode, word: str) -> TrieNode | None:
    current = root
    for char in word:
        if char not in current.children:
            return None
        current = current.children[char]

    if current.is_word:
        return current

    return None


def process_towels(filename: str) -> int:
    input_text = (Path(__file__).parent / filename).read_text()

    input_lines = input_text.splitlines()

    available_towels = {towel.strip() for towel in input_lines[0].split(",")}

    trie = build_trie(available_towels)

    designs = [line.strip() for line in input_lines[2:]]

    return figure_out_how_many_designs_possible(designs, trie)

@cache
def find_prefix_matches(prefix: str, prefix_trie: TrieNode) -> set[str]:
    matches = set()
    if find_trie(prefix_trie, prefix):
        matches.add(prefix)

    return matches

def figure_out_how_many_designs_possible(designs: list[str], prefix_trie: TrieNode) -> int:
    def design_is_possible(design: str, design_index: int) -> bool:
        #print(design[:design_index + 1], design_index, len(design))
        if design_index == len(design):
            #print("Found", design)
            return True
        matches = set()
        for i in range(design_index, len(design) + 1):
            prefix = design[design_index:i]
            matches.update(find_prefix_matches(prefix, prefix_trie))
        sorted_matches = list(reversed(sorted(matches)))
        for match in sorted_matches:
            possible = design_is_possible(design, design_index + len(match))
            if possible:
                return True
        
        return False

    total_possible = 0
    for i, design in enumerate(designs):
        print(f"Processing ({i}/{len(designs)}) {design}")
        if design_is_possible(design, 0):
            total_possible += 1
            print("Design was possible", design)
        else:
            print("Design impossible", design)

    return total_possible

print(process_towels("test2.txt"))