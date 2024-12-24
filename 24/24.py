from pathlib import Path
from typing import Literal, cast
from dataclasses import dataclass
from sympy.parsing.sympy_parser import parse_expr
from functools import cache
import re
import sympy

WireName = str
Computation = Literal["AND", "OR", "XOR"]

def simulate_operations(operations: list[tuple[str, Computation, str, str]], gate_values: dict[str, int]) -> dict[str, int]:
    while operations:
        for operation in operations:
            wire_1 = operation[0]
            wire_2 = operation[2]
            if wire_1 not in gate_values or wire_2 not in gate_values:
                continue

            operations.remove(operation)

            if operation[1] == "AND":
                gate_values[operation[3]] = gate_values[wire_1] & gate_values[wire_2]
            elif operation[1] == "OR":
                gate_values[operation[3]] = gate_values[wire_1] | gate_values[wire_2]
            elif operation[1] == "XOR":
                gate_values[operation[3]] = gate_values[wire_1] ^ gate_values[wire_2]
            else:
                raise ValueError(f"Unknown operation: {operation[1]}")
        
    return gate_values


def do_problem_part_1(filename: str) -> int:
    input = (Path(__file__).parent / filename).read_text().splitlines()
    gate_values = {}
    operations = []
    for line in input:
        if ":" in line:
            name, value = line.split(":")
            gate_values[name] = int(value)
        else:
            matches = re.search(r"(\w+) (\w+) (\w+) -> (\w+)", line)
            if matches:
                operations.append(matches.groups())
    
    gate_values = simulate_operations(operations, gate_values)
    
    z_values = {k: v for k, v in gate_values.items() if k.startswith("z")}
    # sort the z_values
    z_value_sorted_keys = list(reversed(sorted(z_values.keys())))
    # join them to a binary string
    binary_string = "".join(str(z_values[k]) for k in z_value_sorted_keys)
    # convert to int
    return int(binary_string, 2)

@cache
def parse_expression_cached(expression: str) -> sympy.Expr:
    return parse_expr(expression)

def get_carry_expression(wire_name: WireName) -> sympy.Expr:
    assert wire_name.startswith("z")
    z_index = int(wire_name[1:])
    if z_index == -1:
        # We don't have a carry in for the first wire
        return parse_expression_cached("false")
    return parse_expression_cached(f"(x{z_index:02} & y{z_index:02}) | (({get_carry_expression(f"z{z_index - 1:02}")}) & (x{z_index:02} ^ y{z_index:02}))")
    
def get_sum_expression(wire_name: WireName) -> sympy.Expr:
    assert wire_name.startswith("z")
    z_index = int(wire_name[1:])
    return parse_expression_cached(f"x{z_index:02} ^ y{z_index:02} ^ ({get_carry_expression(f"z{z_index - 1:02}")})")

assert get_carry_expression("z00") == parse_expr("(x00 & y00) | (false & (x00 ^ y00))")
assert get_carry_expression("z01") == parse_expr("(x01 & y01) | (x00 & y00 & (x01 ^ y01))")
assert get_carry_expression("z02") == parse_expr("(x02 & y02) | ((x02 ^ y02) & ((x01 & y01) | (x00 & y00 & (x01 ^ y01))))")

assert get_sum_expression("z00") == parse_expr("x00 ^ y00 ^ false")
assert get_sum_expression("z01") == parse_expr("x01 ^ y01 ^ ((x00 & y00) | (false & (x00 ^ y00)))")

assert get_sum_expression("z02") == parse_expr("x02 ^ y02 ^ ((x01 & y01) | (x00 & y00 & (x01 ^ y01)))")

@dataclass
class Node:
    output_wire: WireName # The name of the wire this node is connected to
    def node_is_valid(self) -> bool:
        raise NotImplementedError("node_is_valid not implemented")


@dataclass
class InputDataNode(Node):
    # This would be something like y00 or x05
    pass
    def __str__(self) -> str:
        return self.output_wire
    
    def node_is_valid(self) -> bool:
        return True

@dataclass
class ComputationalNode(Node):
    operation: Computation
    input1: Node
    input2: Node

    def __str__(self) -> str:
        operation_boolean_symbols = {
            "AND": "&",
            "OR": "|",
            "XOR": "^"
        }
        input_1_str = str(self.input1) if isinstance(self.input1, InputDataNode) else f"({self.input1})"
        input_2_str = str(self.input2) if isinstance(self.input2, InputDataNode) else f"({self.input2})"

        return f"({input_1_str}{operation_boolean_symbols[self.operation]}{input_2_str})"
    
    def node_is_valid(self) -> bool:
        original_expression = parse_expr(str(self))
        expected_expression = get_sum_expression(self.output_wire)
        return original_expression == expected_expression
    
def validate_operations(operations: list[tuple[WireName, Computation, WireName, WireName]]) -> None:
    # Check that all wires are unique
    assert len(set(operations)) == len(operations)

    # Check each wire only appears once as an output
    assert len(set([op[3] for op in operations])) == len(operations)

def build_computational_graph(operations: list[tuple[WireName, Computation, WireName, WireName]]) -> dict[WireName, Node]:
    built_nodes: dict[WireName, Node] = {}
    
    operation_by_output_wire: dict[WireName, tuple[WireName, Computation, WireName, WireName]] = {
        op[3]: op for op in operations
    }
    
    def resolve_input(wire_name: WireName) -> Node:
        if wire_name in built_nodes:
            return built_nodes[wire_name]
        if wire_name.startswith("x") or wire_name.startswith("y"):
            built_node: Node = InputDataNode(output_wire=wire_name)
        else:
            # Otherwise, it's a computational node
            # Find the operation that has this wire as an output
            operation = operation_by_output_wire[wire_name]
            input1 = resolve_input(operation[0])
            if input1.output_wire not in built_nodes:
                built_nodes[input1.output_wire] = input1
        
            input2 = resolve_input(operation[2])
            if input2.output_wire not in built_nodes:
                built_nodes[input2.output_wire] = input2

            built_node = ComputationalNode(output_wire=wire_name, operation=operation[1], input1=input1, input2=input2)
            
        built_nodes[wire_name] = built_node
        return built_node

    # Get the remaining operations
    remaining_operations = {op for op in operations if op[3] not in built_nodes}
    for operation in remaining_operations:
        resolve_input(operation[3])


    return built_nodes

def swap_node_wire_names(nodes: dict[WireName, Node], wire_name_1: WireName, wire_name_2: WireName) -> None:
    nodes[wire_name_1], nodes[wire_name_2] = nodes[wire_name_2], nodes[wire_name_1]
    nodes[wire_name_1].output_wire, nodes[wire_name_2].output_wire = wire_name_1, wire_name_2


def do_problem_part_2(filename: str) -> int:
    input = (Path(__file__).parent / filename).read_text().splitlines()
    gate_values = {}
    operations: list[tuple[WireName, Computation, WireName, WireName]] = []
    for line in input:
        if ":" in line:
            name, value = line.split(":")
            gate_values[name] = int(value)
        else:
            matches = re.search(r"(\w+) (\w+) (\w+) -> (\w+)", line)
            if matches:
                operations.append(cast(tuple[WireName, Computation, WireName, WireName], matches.groups()))


    validate_operations(operations)
    built_nodes = build_computational_graph(operations)

    for i in range(46):
        is_valid = built_nodes[f"z{i:02}"].node_is_valid()
        print(f"Z{i} is valid:", is_valid)
        if is_valid:
            continue
        
        print(f"Z{i} is invalid")
        expected_expression = get_sum_expression(f"z{i:02}")
        actual_expression = parse_expr(str(built_nodes[f"z{i:02}"]))
        print("Expected", expected_expression)
        print("Actual", actual_expression)
        node_was_repaired = False
        keys = list(built_nodes.keys())
        keys = [k for k in keys if not k.startswith("x") and not k.startswith("y")]
        for cwi, candidate_wire_one in enumerate(keys):
            print(f"Trying {candidate_wire_one}, {cwi}/{len(keys)}")
            for cwi2, candidate_wire_two in enumerate(keys):
                if cwi2 <= cwi:
                    continue
                swap_node_wire_names(built_nodes, candidate_wire_one, candidate_wire_two)
                node_repaired = built_nodes[f"z{i:02}"].node_is_valid()
                if node_repaired:
                    print(f"{candidate_wire_one} is the wire that would work")
                    node_was_repaired = True
                    break
                else:
                    # Swap back
                    swap_node_wire_names(built_nodes, candidate_wire_one, candidate_wire_two)
            if node_was_repaired:
                break

            
        if not node_was_repaired:
            raise ValueError(f"Failed to repair node z{i:02}")
    
    return 0


    

# Monkey only sells after looking for a specific sequence of four consecutive changes in price
# First price has no change due to lack of comparison
# Find the highest 4-seq to get the most bananas across all buyers
# Each buyer gets 2000 price changes


#print("part 1 answer", do_problem_part_1("input.txt"))
print("part 2 answer", do_problem_part_2("input.txt"))