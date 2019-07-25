import enum

MAX_SIGNED_VALUE = 2 ** 7
MAX_UNSIGNED_VALUE = 2 ** 8


class AddressingMode(enum.Enum):
    immediate = enum.auto()
    absolute = enum.auto()


class Cpu:
    """6502 cpu

    - 8 bit cpu, with 16 bit address bus
    - little endian ie. value of 18 is stored as 0x0201
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

    def add_with_carry(self, addressing_mode: enum.Enum, data: int) -> None:
        if addressing_mode == AddressingMode.immediate:
            self._add_with_carry_immediate(data)
        elif addressing_mode == AddressingMode.absolute:
            self._add_with_carry_absolute(data)

    def _add_with_carry_immediate(self, value: int) -> None:
        result = self.accumulator + value
        if result >= MAX_SIGNED_VALUE:
            self.processor_status_carry = True
            result = result % MAX_SIGNED_VALUE

        if result == 0:
            self.processor_status_zero = True
        self.accumulator = result

    def _add_with_carry_absolute(self, value: int) -> None:
        value = self.read_from_memory(value)
        return self._add_with_carry_immediate(value)

    def read_from_memory(self, address: int) -> int:
        return self.memory[address]
