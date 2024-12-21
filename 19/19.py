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
    reverse_trie = build_trie({t[::-1] for t in available_towels})

    designs = [line.strip() for line in input_lines[2:]]

    return figure_out_how_many_designs_possible(designs, trie, reverse_trie)

@cache
def find_prefix_matches(prefix: str, prefix_trie: TrieNode) -> set[str]:
    matches = set()
    if find_trie(prefix_trie, prefix):
        matches.add(prefix)

    return matches

def design_is_possible(design: str, towel_trie_root: TrieNode) -> bool:
    recursion_stack = [0]
    iterations = 0
    design = design[::-1]
    while len(recursion_stack) > 0:
        design_index = recursion_stack.pop()
        if design_index == len(design):
            return True
        
        # Crawl down the trie until there is nothing more
        current_node = towel_trie_root
        for i in range(design_index, len(design)):
            char = design[i]
            if char not in current_node.children:
                # We have gotten to the point in the loop where there are no more prefix matches
                break
            current_node = current_node.children[char]
            if current_node.is_word:
                # We append one to i to represent everything up to i is covered
                recursion_stack.append(i + 1)
        # We should have now appended all potential starting positions to the recursion stack
        iterations += 1
        if iterations % 100_000_00 == 0:
            print(iterations)
    return False

# TODO: There is an inherent symmetry to the problem, if a certain word is having a lot if iterations one way,
# we can construct it from the other end

ITERATION_LIMIT = 1_000_000

def design_is_possible_hacky_forward_backwards(original_design: str, forwards_trie: TrieNode, reverse_trie: TrieNode) -> bool | None:
    def check_one_way_exit_early(design: str, trie: TrieNode) -> bool | None:
        recursion_stack = [0]
        iterations = 0

        while len(recursion_stack) > 0:
            design_index = recursion_stack.pop()
            if design_index == len(design):
                return True

                # Crawl down the trie until there is nothing more
            current_node = trie
            for i in range(design_index, len(design)):
                char = design[i]
                if char not in current_node.children:
                    # We have gotten to the point in the loop where there are no more prefix matches
                    break
                current_node = current_node.children[char]
                if current_node.is_word:
                    # We append one to i to represent everything up to i is covered
                    recursion_stack.append(i + 1)
            # We should have now appended all potential starting positions to the recursion stack
            iterations += 1
            if iterations > ITERATION_LIMIT:
                return None
            
        return False
    
    forwards = check_one_way_exit_early(original_design, forwards_trie)
    if forwards is None:
        backwards = check_one_way_exit_early(original_design[::-1], reverse_trie)
        return backwards        
    else:
        return forwards     
    
def figure_out_how_many_designs_possible(designs: list[str], trie: TrieNode, reverse_trie: TrieNode) -> int:
    total_possible = 0
    for i, design in enumerate(designs):
        print(f"Processing ({i}/{len(designs)}) {design}")
        heuristic = design_is_possible_hacky_forward_backwards(design, trie, reverse_trie)
        if heuristic is None:
            print("Not sure")
            final = design_is_possible(design, trie)
            if final:
                total_possible += 1
                print("Design was possible", design)
            else:
                print("Design impossible", design)
        total_possible += 1 if heuristic else 0
    return total_possible

print(process_towels("input.txt"))