import enum

MAX_UNSIGNED_VALUE = 2 ** 8


class AddressingMode(enum.Enum):
    immediate = enum.auto()
    absolute = enum.auto()
    zero_page = enum.auto()
    accumulator = enum.auto()


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
        self.processor_status_carry: bool = False
        self.processor_status_zero: bool = False
        self.processor_status_interrupt_disable: bool = False
        self.processor_status_decimal_mode: bool = False
        self.processor_status_break_command: bool = False
        self.processor_status_overflow: bool = False
        self.processor_status_negative: bool = False
        self.memory: bytearray = bytearray()

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
        self.processor_status_carry = bool(result & 0x100)

        # Check for overflow (only applies to signed arithmetic).
        # Will only occur if arguments are the same sign (increased magnitude)
        arg1_sign_bit = arg1 & 0x80
        value_sign_bit = value & 0x80
        result_sign_bit = result & 0x80

        # If params are the same sign, addition will increase the magnitude of result and with same sign If the sign
        # bit of result is different, then there is overflow
        self.processor_status_overflow = bool((arg1_sign_bit & value_sign_bit) ^ result_sign_bit)

        # Check the MSB for negative value
        self.processor_status_negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.processor_status_zero = self.accumulator == 0

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
        self.processor_status_negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.processor_status_zero = self.accumulator == 0

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
        self.processor_status_carry = bool(result & 0x100)

        # Check the MSB for negative value
        self.processor_status_negative = bool(result & 0x80)

        # Result is only 8 bit, must modulo it to fit register
        self.accumulator = result % MAX_UNSIGNED_VALUE

        # Check if the entire register is zero. Or just use int comparison
        self.processor_status_zero = self.accumulator == 0
