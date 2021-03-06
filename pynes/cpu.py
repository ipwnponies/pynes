import enum
from dataclasses import dataclass

from pynes.addressing_mode import AddressingMode
from pynes.instructions import add
from pynes.instructions import and_
from pynes.instructions import asl
from pynes.instructions import branch
from pynes.instructions import cmp

MAX_UNSIGNED_VALUE = 2 ** 8


class StatusFlag(enum.Enum):
    carry = enum.auto()
    zero = enum.auto()
    interrupt_disable = enum.auto()
    decimal = enum.auto()
    break_ = enum.auto()
    overflow = enum.auto()
    negative = enum.auto()


@dataclass
class StatusRegister:
    carry: bool = False
    zero: bool = False
    interrupt_disable: bool = False
    decimal: bool = False
    break_: bool = False
    overflow: bool = False
    negative: bool = False


class Cpu:
    """6502 cpu

    - 8 bit cpu, with 16 bit address bus
    - little endian ie. value of 18 is stored as 0x0201
    - status register
    - program counter
    - stack and stack pointer
    - x, y and accumulator register. 8-bit registers that have semantic meaning and use
    """

    def __init__(self) -> None:
        self.program_counter: int = 0  # 16 bit
        self.stack_pointer: int = 0  # 16 bit
        self.stack: int = 0  # 256 byte
        self.accumulator: int = 0  # 8 bit
        self.register_x: int = 0  # 8 bit
        self.register_y: int = 0  # 8 bit
        self.status = StatusRegister()
        self.memory = bytearray()

    def decode_instruction(self, opcode: int) -> None:  # pragma: no cover
        """This function is currently a stub, will eventually be the only way to reference instructions."""
        if opcode == 'PLACEHOLDER for add':
            addressing_mode = AddressingMode.immediate
            data = 0x0
            add.add_with_carry(self, addressing_mode, data)
        elif opcode == 'PLACEHOLDER for and':
            addressing_mode = AddressingMode.immediate
            data = 0x0
            and_.and_(self, addressing_mode, data)
        elif opcode == 'PLACEHOLDER for asl':
            addressing_mode = AddressingMode.immediate
            data = 0x0
            asl.asl(self, addressing_mode)
        elif opcode == 'PLACEHOLDER for branch':
            data = 0x0
            branch.branch_if_carry_clear(self, data)
        elif opcode == 'PLACEHOLDER for cmp':
            data = 0x0
            cmp.cmp(self, data)

    def read_from_memory(self, address: int) -> int:
        return self.memory[address]
