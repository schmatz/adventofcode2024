OPCODES = {
    0b000: "adv", # Division
    0b001: "bxl", # Bitwise XOR
    0b010: "bst", # Combo operand modulo 8, write B
    0b011: "jnz", # Nothing if A register is 0, otherwise sets IP to value of literal operand, if jump no increment ip
    0b100: "bxc", # Calculate bitwise XOR of register B and register C, then store in B. Reads operand but ignores
    0b101: "out", # Calculate the value of its combo operand modulo 8, then ouptuts that value (if multiple values, separated by commas)
    0b110: "bdv", # Exactly like the adv instruction, but register is stored in C register
    0b111: "cdv", # Cdv
}

def parse_input(filename: str) -> tuple[dict[str, int], list[int]]:
    with open(filename) as f:
        input_text = f.read()

    lines = input_text.splitlines()
    registers = {}
    registers["A"] = int(lines[0].split(":")[1].strip())
    registers["B"] = int(lines[1].split(":")[1].strip())
    registers["C"] = int(lines[2].split(":")[1].strip())

    program = [int(num) for num in lines[4].split(":")[1].split(",")]

    return (registers, program)

def resolve_combo_operand(registers: dict[str,int], combo_operand: int) -> int:
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
    denominator =  2 ** resolve_combo_operand(registers, operand)
    registers[target_register] = numerator // denominator

def run_program(filename: str) -> str:
    registers, program = parse_input(filename)

    instruction_pointer = 0
    final_output: list[str] = []
    while instruction_pointer < len(program):
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
                    instruction_pointer = operand - 2 # because we will increment
            case "bxc":
                registers["B"] ^= registers["C"]
            case "out":
                final_output.append(str(resolve_combo_operand(registers, operand) % 8))
            case "bdv":
                do_div(registers, operand, "B")
            case "cdv":
                do_div(registers, operand, "C")
            case _:
                raise AssertionError("Invalid opcode")
        instruction_pointer += 2

    return ",".join(final_output)


#assert run_program("test1.txt") == "4,6,3,5,6,3,5,2,1,0"
#assert run_program("input.txt")  == "1,4,6,1,6,4,3,0,3"
print(run_program("test2.txt"))