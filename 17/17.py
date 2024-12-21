import time 
from pathlib import Path


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
    input_text = (Path(__file__).parent / filename).read_text()

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

# Run one timestep, returning the new IP
def step_forward(registers: dict[str, int], instruction_pointer: int, program: list[int], final_output: list[int]) -> int:
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
        instruction_pointer = step_forward(registers, instruction_pointer, program, final_output)

    return final_output


def input_program_optimized(registerA: int) -> list[int]:
    a = registerA
    output = []
    while True:
        # We can make this number up
        a_3_lower_bits = a & 0b111
        a_3_lower_bits_negated = (~a_3_lower_bits) & 0b111

        # This relies on the next N bits
        a_shifted_by_a_3_lower_bits_negated = (a >> a_3_lower_bits_negated) & 0b111

        b = a_3_lower_bits ^ a_shifted_by_a_3_lower_bits_negated

        # Inverse of xor is xor itself
        output.append(b)

        a >>= 3
        if a == 0:
            break

    return output

def reverse_program_search(filename: str) -> int:
    full_program = [2,4,1,7,7,5,1,7,4,6,0,3,5,5,3,0]
    current_number = 0b000

    def find_combo(program_index: int, current_number: int) -> int:
        if program_index == 0:
            return current_number
        
        target_output = full_program[program_index:]

        for i in range(0b000, 0b1000):
            candidate_number = (current_number << 3) | i 

            output = input_program_optimized(candidate_number)

            if output == target_output:
                print(f"Candidate {candidate_number:b} results in output {target_output}")
                current_number = (current_number << 3 | i)
                retval = find_combo(program_index - 1, current_number)
                if retval != -1:
                    return retval

        return -1
    return find_combo(len(full_program) - 1, current_number)


def run_program_to_find_quine(filename: str) -> int:
    registers, program = parse_input(filename)

    program_length = len(program)
    min_a = 8 ** program_length
    max_a = 8 ** (program_length + 1)
    
    for a in range(min_a, max_a):
        # Run optimized program
        output_index = 0
        while output_index < program_length:
            if (a & 7) ^ ((a >> ((a & 7) ^ 7)) & 7) == program[output_index]:
                output_index += 1
            else:
                break
                
            a >>= 3
            if a == 0:
                break

        if output_index == program_length:
            return a
        
        if (a & ((1 << 30) - 1)) == 0:
            print(a)
    
    return -1
            
        
#assert run_program("test1.txt") == "4,6,3,5,6,3,5,2,1,0"
#assert run_program("input.txt")  == "1,4,6,1,6,4,3,0,3"
print(run_program("input.txt"))
#print(run_program_to_find_quine("input.txt"))
#input_program_optimized()
print(reverse_program_search("input.txt"))