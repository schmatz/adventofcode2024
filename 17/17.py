from pathlib import Path


OPCODES = {
    0b000: "adv",  # Division
    0b001: "bxl",  # Bitwise XOR
    0b010: "bst",  # Combo operand modulo 8, write B
    0b011: "jnz",  # Nothing if A register is 0, otherwise sets IP to value of literal operand, if jump no increment ip
    0b100: "bxc",  # Calculate bitwise XOR of register B and register C, then store in B. Reads operand but ignores
    0b101: "out",  # Calculate the value of its combo operand modulo 8, then ouptuts that value (if multiple values, separated by commas)
    0b110: "bdv",  # Exactly like the adv instruction, but register is stored in C register
    0b111: "cdv",  # Cdv
}


def parse_input(filename: str) -> tuple[dict[str, int], list[int]]:
    input_text = (Path(__file__).parent / filename).read_text()

    lines = input_text.splitlines()
    registers = {}
    registers["A"] = int(lines[0].split(":")[1].strip())
    registers["B"] = int(lines[1].split(":")[1].strip())
    registers["C"] = int(lines[2].split(":")[1].strip())

    program = [int(num) for num in lines[4].split(":")[1].split(",")]

    return (registers, program)


def resolve_combo_operand(registers: dict[str, int], combo_operand: int) -> int:
    match combo_operand:
        case _ if combo_operand < 4:
            return combo_operand
        case 4:
            return registers["A"]
        case 5:
            return registers["B"]
        case 6:
            return registers["C"]
        case _:
            raise AssertionError("Shouldn't happen with combo operand")


def do_div(registers: dict[str, int], operand: int, target_register: str):
    numerator = registers["A"]
    denominator = 2 ** resolve_combo_operand(registers, operand)
    registers[target_register] = numerator // denominator


# Run one timestep, returning the new IP
def step_forward(
    registers: dict[str, int],
    instruction_pointer: int,
    program: list[int],
    final_output: list[int],
) -> int:
    opcode = program[instruction_pointer]
    operand = program[instruction_pointer + 1]

    match OPCODES[opcode]:
        case "adv":
            do_div(registers, operand, "A")
        case "bxl":
            registers["B"] ^= operand
        case "bst":
            registers["B"] = resolve_combo_operand(registers, operand) % 8
        case "jnz":
            if registers["A"] != 0 and operand != instruction_pointer:
                instruction_pointer = operand - 2  # because we will increment
        case "bxc":
            registers["B"] ^= registers["C"]
        case "out":
            final_output.append(resolve_combo_operand(registers, operand) % 8)
        case "bdv":
            do_div(registers, operand, "B")
        case "cdv":
            do_div(registers, operand, "C")
        case _:
            raise AssertionError("Invalid opcode")
    instruction_pointer += 2
    return instruction_pointer


def run_program(filename: str) -> list[int]:
    registers, program = parse_input(filename)

    instruction_pointer = 0
    final_output: list[int] = []
    while instruction_pointer < len(program):
        instruction_pointer = step_forward(
            registers, instruction_pointer, program, final_output
        )

    return final_output


def input_program_optimized_simple(a: int) -> list[int]:
    output = []
    while True:
        b = a & 0b111  # B = A % 8
        b = b ^ 0b111  # B = B ^ 7
        c = a >> b  # C = A // (2 ** B) or A >> B
        b = b ^ 0b111  # B = B ^ 7
        b = b ^ c  # B = B ^ C
        output.append(b & 0b111)  # output(B % 8)
        a = a >> 3  # A = A >> 3

        if a == 0:
            break
    return output


FULL_TARGET_PROGRAM = [2, 4, 1, 7, 7, 5, 1, 7, 4, 6, 0, 3, 5, 5, 3, 0]


# Find *every* program that outputs the target [0]
# for each one of those, find every one that outputs the target [3,0]
# For everyone one of those, find every one that outputs [5,3,0]
def quine_program_search() -> set[int]:
    def find_register_a(target_output: list[int], a_prefix: int) -> set[int]:
        working_additions: set[int] = set()
        for i in range(0b000, 0b1000):
            a = (a_prefix << 3) | i

            actual_output = input_program_optimized_simple(a)

            if actual_output == target_output:
                working_additions.add(i)

        if target_output == FULL_TARGET_PROGRAM:
            return {a_prefix << 3 | num for num in working_additions}

        final_set = set()
        for num in working_additions:
            expanded_numbers = find_register_a(
                FULL_TARGET_PROGRAM[
                    len(FULL_TARGET_PROGRAM) - len(target_output) - 1 :
                ],
                (a_prefix << 3) | num,
            )
            if expanded_numbers:
                print(
                    "Found expanded numbers",
                    expanded_numbers,
                    "for output",
                    target_output,
                )
            final_set.update(expanded_numbers)

        return final_set

    return find_register_a([0], 0b000)


assert run_program("test1.txt") == [4, 6, 3, 5, 6, 3, 5, 2, 1, 0]
input_program_good_output = [1, 4, 6, 1, 6, 4, 3, 0, 3]
assert run_program("input.txt") == input_program_good_output
assert input_program_optimized_simple(66245665) == input_program_good_output
assert input_program_optimized_simple(0b111010110000000000) == [0, 3, 5, 5, 3, 0]

### Now that we have deduced we have understood the program, let's search for the golden quine output
candidate_numbers = quine_program_search()
for candidate_number in candidate_numbers:
    program_output = input_program_optimized_simple(candidate_number)
    assert program_output == FULL_TARGET_PROGRAM


# assert program_output == FULL_TARGET_PROGRAM
print("Got it!", min(candidate_numbers))
