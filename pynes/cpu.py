import enum
from dataclasses import dataclass

MAX_UNSIGNED_VALUE = 2 ** 8


class AddressingMode(enum.Enum):
    immediate = enum.auto()
    absolute = enum.auto()
    zero_page = enum.auto()
    accumulator = enum.auto()


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

    def add_with_carry(self, addressing_mode: AddressingMode, data: int) -> None:
        """Add instruction

        Overflow is handled with two status flags: carry for unsigned addition and overflow for signed addition.
        """
        if addressing_mode == AddressingMode.immediate:
            self._add_with_carry_immediate(data)
        elif addressing_mode == AddressingMode.absolute:
            self._add_with_carry_absolute(data)
        elif addressing_mode == AddressingMode.zero_page:
            # If you only specify the last byte of address, this automagically becomes equivalent to absolute
            # Adding here for completeness but this is very much a hardware optimization, that looks non-functional
            # in python.
            self._add_with_carry_absolute(data)
        else:
            raise NotImplementedError()

    def _add_with_carry_immediate(self, value: int) -> None:
        arg1 = self.accumulator
        result = arg1 + value

        # If 9th bit is set, then there is carry. This only applies to unsigned arithmetic.
        self.status.carry = bool(result & 0x100)

        # Check for overflow (only applies to signed arithmetic).
        # Will only occur if arguments are the same sign (increased magnitude)
        arg1_sign_bit = arg1 & 0x80
        value_sign_bit = value & 0x80
        result_sign_bit = result & 0x80

        # If params are the same sign, addition will increase the magnitude of result and with same sign If the sign
        # bit of result is different, then there is overflow
        self.status.overflow = bool((arg1_sign_bit & value_sign_bit) ^ result_sign_bit)

        # Check the MSB for negative value
        self.status.negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.status.zero = self.accumulator == 0

    def _add_with_carry_absolute(self, value: int) -> None:
        value = self.read_from_memory(value)
        return self._add_with_carry_immediate(value)

    def read_from_memory(self, address: int) -> int:
        return self.memory[address]

    def _and(self, addressing_mode: AddressingMode, value: int) -> None:
        if addressing_mode == AddressingMode.immediate:
            self._and_immediate(value)
        elif addressing_mode == AddressingMode.absolute:
            self._and_absolute(value)
        elif addressing_mode == AddressingMode.zero_page:
            # If you only specify the last byte of address, this automagically becomes equivalent to absolute
            # Adding here for completeness but this is very much a hardware optimization, that looks non-functional
            # in python.
            self._and_absolute(value)
        else:
            raise NotImplementedError()

    def _and_immediate(self, value: int) -> None:
        arg1 = self.accumulator
        result = arg1 & value

        # Check the MSB for negative value
        self.status.negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.status.zero = self.accumulator == 0

    def _and_absolute(self, value: int) -> None:
        value = self.read_from_memory(value)
        return self._and_immediate(value)

    def asl(self, addressing_mode: AddressingMode) -> None:
        """Arithmetic shift left

        0 is shifted into LSB and MSB is shifted into carry flag.
        """
        if addressing_mode == AddressingMode.accumulator:
            self._asl_accumulator()
        else:
            raise NotImplementedError()

    def _asl_accumulator(self) -> None:
        """ASL accumulator"""
        arg = self.accumulator
        result = arg << 1

        # Check the previous MSB for carry value
        self.status.carry = bool(result & 0x100)

        # Check the MSB for negative value
        self.status.negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.status.zero = self.accumulator == 0

    def branch_if_carry_clear(self, value: int) -> None:
        """BCC instruction"""
        self._branch(not self.status.carry, value)

    def branch_if_carry_set(self, value: int) -> None:
        """BCS instruction"""
        self._branch(self.status.carry, value)

    def branch_if_equal(self, value: int) -> None:
        """BEQ instruction"""
        self._branch(self.status.zero, value)

    def branch_if_minus(self, value: int) -> None:
        """BMI instruction"""
        self._branch(self.status.negative, value)

    def branch_if_not_equal(self, value: int) -> None:
        """BNE instruction"""
        self._branch(not self.status.zero, value)

    def branch_if_positive(self, value: int) -> None:
        """BPL instruction"""
        self._branch(not self.status.negative, value)

    def branch_if_overflow_clear(self, value: int) -> None:
        """BVC instruction"""
        self._branch(not self.status.overflow, value)

    def branch_if_overflow_set(self, value: int) -> None:
        """BVS instruction"""
        self._branch(self.status.overflow, value)

    def _branch(self, predicate_for_branch: bool, value: int) -> None:
        if predicate_for_branch:
            self.program_counter += value

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
