import enum
from typing import Any


class AddressingMode(enum.Enum):
    immediate = enum.auto()


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

    def add_with_carry(self, addressing_mode: enum.Enum, data: Any) -> None:
        if addressing_mode == AddressingMode.immediate:
            self._add_with_carry_immediate(data)

    def _add_with_carry_immediate(self, value: int) -> None:
        result = self.accumulator + value
        self.accumulator = result
