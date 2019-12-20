"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
POP = 0b01000110
PUSH = 0b01000101

# TODO
# Add CMP instruction and equal flag
# add JMP instruction   
# add JEQ 
# add JNE

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.sp = 7
        self.E = 0
        self.L = 0
        self.G = 0
        self.commands = {
            "HLT": 0b00000001,
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "MUL": 0b10100010,
            "ADD": 0b10100000,
            "POP": 0b01000110,
            "PUSH": 0b01000101,
            "CALL": 0b01010000,
            "RET": 0b00010001,
            "CMP": 0b10100111,
            "JMP": 0b01010100,
            "JEQ": 0b01010101,
            "JNE": 0b01010110
        }

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        with open(filename) as f:
            for line in f:
                n = line.split("#")
                n[0] = n[0].strip()

                if n[0] == '':
                    continue

                val = int(n[0], 2)
                self.ram[address] = val
                address += 1

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL": 
            self.register[reg_a] *= self.register[reg_b]
        elif op == "CMP": 
            # set E flag to 1 if equal
            if self.register[reg_a] == self.register[reg_b]:
                self.E = 1

            # set L flag to 1 if less than
            if self.register[reg_a] < self.register[reg_b]:
                self.L = 1

            # set G flag to 1 if greater than
            if self.register[reg_a] > self.register[reg_b]:
                self.G = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        halted = False

        while not halted:
            instruction = self.ram[self.pc]

            if instruction == self.commands["LDI"]: # LDI R0,8
                operand_a  = self.ram[self.pc + 1] # get position
                operand_b = self.ram[self.pc + 2] # get value to store
                self.register[operand_a] = operand_b # save value into register
                self.pc += 3 # increase pc position by 2
            
            elif instruction == self.commands["PRN"]: # PRN R0
                position = self.ram[self.pc + 1] # get position of number to pring
                print(self.register[position]) # print value at given position
                self.pc += 1 # increase pc value by 1

            elif instruction == self.commands["MUL"]: # MUL
                operand_a  = self.ram[self.pc + 1] # get position
                operand_b = self.ram[self.pc + 2] # get value to store
                self.alu("MUL", operand_a, operand_b) # increase pc by 1
                self.pc += 3 # increase pc position by 2

            elif instruction == self.commands["ADD"]: # MUL
                operand_a  = self.ram[self.pc + 1] # get position
                operand_b = self.ram[self.pc + 2] # get value to store
                self.alu("ADD", operand_a, operand_b) # increase pc by 1
                self.pc += 3 # increase pc position by 2

            elif instruction == self.commands["PUSH"]: # PUSH
                operand_a = self.ram[self.pc + 1] # gives the position of value to push
                value = self.register[operand_a] # get value to to push from register
                self.sp -= 1
                self.ram[self.sp] = value
                self.pc += 2

            elif instruction == self.commands["POP"]: # POP
                operand_a = self.ram[self.pc + 1] # gives what register I want save the value I popped
                value = self.ram[self.sp] # gets last value from stack
                self.register[operand_a] = value # registers popped value into register
                self.sp += 1 # increase stack pointer
                self.pc += 2 # instructions pointer goes up 2

            elif instruction == self.commands["CALL"]: # CALL
                reg_a = self.register[self.ram[self.pc + 1]] # here we save into variable the position we need to skip to
                self.sp -= 1 # we decrease stack pointer to save new value 
                self.ram[self.sp] = self.pc + 2 # We save into ram the next instruction index we must come back to after call into stack
                self.pc = reg_a  # We jump to instruction index

            elif instruction == self.commands["RET"]: # RET
                return_address = self.ram[self.sp] # we grab return adress from stack
                self.ram[self.sp] += 1 # increase instructions pointer by 1
                self.pc = return_address # point pc pointer back to return address
            
#----------------------------------------- SPRINT CHALLENGE

            elif instruction == self.commands["CMP"]: 
                operand_a  = self.ram[self.pc + 1] # get position
                operand_b = self.ram[self.pc + 2] # get value to store
                self.alu("CMP", operand_a, operand_b) # increase pc by 1
                self.pc += 3 # increase pc position by 2

            elif instruction == self.commands["JMP"]: 
                operand_a  = self.ram[self.pc + 1] # get register
                self.pc = self.register[operand_a] # move pc to position stored in register

            elif instruction == self.commands["JEQ"]: 
                if self.E == 1:
                    operand_a  = self.ram[self.pc + 1] # get register
                    self.pc = self.register[operand_a] # move pc to position stored in register
                else:
                    self.pc += 2

            elif instruction == self.commands["JNE"]: 
                if self.E == 0:
                    operand_a  = self.ram[self.pc + 1] # get register
                    self.pc = self.register[operand_a] # move pc to position stored in register
                else:
                    self.pc += 2

            elif instruction == self.commands["HLT"]: # HLT
                halted = True # halt while loop
                self.pc += 1 # increase pc by 1
            
            else:
                self.pc += 1 # if no commands match then increase pc by 1


    def ram_read(self, position):
        """Run the CPU."""
        return self.ram[position]

    def ram_write(self, position, value):
        """Run the CPU."""
        self.ram[position] = value
