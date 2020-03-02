from typing import TYPE_CHECKING

from pynes.addressing_mode import AddressingMode

MAX_UNSIGNED_VALUE = 2 ** 8

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def and_(cpu: 'Cpu', addressing_mode: AddressingMode, value: int) -> None:
    if addressing_mode == AddressingMode.immediate:
        and_immediate(cpu, value)
    elif addressing_mode == AddressingMode.absolute:
        and_absolute(cpu, value)
    elif addressing_mode == AddressingMode.zero_page:
        # If you only specify the last byte of address, this automagically becomes equivalent to absolute
        # Adding here for completeness but this is very much a hardware optimization, that looks non-functional
        # in python.
        and_absolute(cpu, value)
    else:
        raise NotImplementedError()


def and_immediate(cpu: 'Cpu', value: int) -> None:
    arg1 = cpu.accumulator
    result = arg1 & value

    # Check the MSB for negative value
    cpu.status.negative = bool(result & 0x80)

    # Result is only 8 bit, must modulo it to fit register
    cpu.accumulator = result % MAX_UNSIGNED_VALUE

    # Check if the entire register is zero. Or just use int comparison
    cpu.status.zero = cpu.accumulator == 0


def and_absolute(cpu: 'Cpu', value: int) -> None:
    value = cpu.read_from_memory(value)
    return and_immediate(cpu, value)
