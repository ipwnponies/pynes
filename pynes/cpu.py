import enum
from dataclasses import dataclass

from pynes.addressing_mode import AddressingMode
from pynes.instructions import add
from pynes.instructions import and_
from pynes.instructions import asl
from pynes.instructions import branch

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

    def read_from_memory(self, address: int) -> int:
        return self.memory[address]

    def bit(self, value: int) -> None:
        """Bitmask operation

        Bitmask pattern is located in accumulator and memory value is target.
        This is really an AND operation, for bitmasking purposes."""
        arg1 = self.accumulator
        arg2 = self.read_from_memory(value)

        # Set zero flag if bitmask masks everything
        self.status.zero = not arg1 & arg2
        self.status.negative = bool(1 << 7 & arg2)
        self.status.overflow = bool(1 << 6 & arg2)

    def clear_carry(self) -> None:
        self._clear_flag(StatusFlag.carry)

    def clear_decimal(self) -> None:
        self._clear_flag(StatusFlag.decimal)

    def clear_interrupt(self) -> None:
        self._clear_flag(StatusFlag.interrupt_disable)

    def clear_overflow(self) -> None:
        self._clear_flag(StatusFlag.overflow)

    def _clear_flag(self, flag: StatusFlag) -> None:
        """Clear carry status flag."""
        if flag == StatusFlag.carry:
            self.status.carry = False
        elif flag == StatusFlag.decimal:
            self.status.decimal = False
        elif flag == StatusFlag.interrupt_disable:
            self.status.interrupt_disable = False
        elif flag == StatusFlag.overflow:
            self.status.overflow = False
        else:
            raise NotImplementedError(f'{flag} mode is not supported')

    def cmp(self, value: int) -> None:
        self._compare(self.accumulator, value)

    def cpx(self, value: int) -> None:
        self._compare(self.register_x, value)

    def cpy(self, value: int) -> None:
        self._compare(self.register_y, value)

    def _compare(self, arg1: int, value: int) -> None:
        """Compare accumulator against memory value."""
        arg2 = self.read_from_memory(value)

        result = arg1 - arg2

        self.status.carry = result > 0
        self.status.zero = result == 0
        self.status.negative = result < 0
