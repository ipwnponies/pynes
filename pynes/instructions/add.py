from typing import TYPE_CHECKING

from pynes.addressing_mode import AddressingMode

MAX_UNSIGNED_VALUE = 2 ** 8

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def add_with_carry(cpu: 'Cpu', addressing_mode: AddressingMode, data: int) -> None:
    """Add instruction

    Overflow is handled with two status flags: carry for unsigned addition and overflow for signed addition.
    """
    if addressing_mode == AddressingMode.immediate:
        _add_with_carry_immediate(cpu, data)
    elif addressing_mode == AddressingMode.absolute:
        _add_with_carry_absolute(cpu, data)
    elif addressing_mode == AddressingMode.zero_page:
        # If you only specify the last byte of address, this automagically becomes equivalent to absolute
        # Adding here for completeness but this is very much a hardware optimization, that looks non-functional
        # in python.
        _add_with_carry_absolute(cpu, data)
    else:
        raise NotImplementedError()


def _add_with_carry_immediate(cpu: 'Cpu', value: int) -> None:
    arg1 = cpu.accumulator
    result = arg1 + value

    # If 9th bit is set, then there is carry. This only applies to unsigned arithmetic.
    cpu.status.carry = bool(result & 0x100)

    # Check for overflow (only applies to signed arithmetic).
    # Will only occur if arguments are the same sign (increased magnitude)
    arg1_sign_bit = arg1 & 0x80
    value_sign_bit = value & 0x80
    result_sign_bit = result & 0x80

    # If params are the same sign, addition will increase the magnitude of result and with same sign If the sign
    # bit of result is different, then there is overflow
    cpu.status.overflow = bool((arg1_sign_bit & value_sign_bit) ^ result_sign_bit)

    # Check the MSB for negative value
    cpu.status.negative = bool(result & 0x80)

    # Result is only 8 bit, must modulo it to fit register
    cpu.accumulator = result % MAX_UNSIGNED_VALUE

    # Check if the entire register is zero. Or just use int comparison
    cpu.status.zero = cpu.accumulator == 0


def _add_with_carry_absolute(cpu: 'Cpu', value: int) -> None:
    value = cpu.read_from_memory(value)
    return _add_with_carry_immediate(cpu, value)
