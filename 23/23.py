from pathlib import Path
from itertools import permutations
from functools import cache
from typing import Literal, cast
from collections import deque, defaultdict, Counter
import networkx as nx


def find_networks_of_three(
    connections: dict[str, set[str]],
) -> set[tuple[str, str, str]]:
    all_networks_of_three = set()
    for computer_a in connections:
        for computer_b in connections[computer_a]:
            for computer_c in connections[computer_b]:
                if computer_c in connections[computer_a]:
                    all_networks_of_three.add(
                        cast(
                            tuple[str, str, str],
                            tuple(sorted([computer_a, computer_b, computer_c])),
                        )
                    )
    return all_networks_of_three


def find_largest_graph_clique(connections: dict[str, set[str]]) -> set[str]:
    G = nx.Graph()
    for computer_id, connected_computers in connections.items():
        G.add_node(computer_id)
        for connected_computer in connected_computers:
            G.add_edge(computer_id, connected_computer)

    largest_clique = max(nx.find_cliques(G), key=len)
    return set(largest_clique)


def do_problem(filename: str) -> int:
    input = (Path(__file__).parent / filename).read_text().splitlines()
    computer_tuples: list[tuple[str, str]] = [
        cast(tuple[str, str], tuple(line.strip().split("-"))) for line in input
    ]

    connections: dict[str, set[str]] = defaultdict(set)

    for a, b in computer_tuples:
        connections[a].add(b)
        connections[b].add(a)

    all_networks_of_three = find_networks_of_three(connections)

    num_connections_including_historian = sum(
        [
            1
            for network in all_networks_of_three
            if network[0].startswith("t")
            or network[1].startswith("t")
            or network[2].startswith("t")
        ]
    )

    print(num_connections_including_historian)

    largest_subnetwork = find_largest_graph_clique(connections)
    password = ",".join([name for name in sorted(largest_subnetwork)])
    print(password)

    return num_connections_including_historian


# Monkey only sells after looking for a specific sequence of four consecutive changes in price
# First price has no change due to lack of comparison
# Find the highest 4-seq to get the most bananas across all buyers
# Each buyer gets 2000 price changes


print("part 1 answer", do_problem("input.txt"))
