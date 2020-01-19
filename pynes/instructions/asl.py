from typing import TYPE_CHECKING

from pynes.addressing_mode import AddressingMode

MAX_UNSIGNED_VALUE = 2 ** 8

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def asl(cpu: 'Cpu', addressing_mode: AddressingMode) -> None:
    """Arithmetic shift left

    0 is shifted into LSB and MSB is shifted into carry flag.
    """
    if addressing_mode == AddressingMode.accumulator:
        _asl_accumulator(cpu)
    else:
        raise NotImplementedError()


def _asl_accumulator(cpu: 'Cpu') -> None:
    """ASL accumulator"""
    arg = cpu.accumulator
    result = arg << 1

    # Check the previous MSB for carry value
    cpu.status.carry = bool(result & 0x100)

    # Check the MSB for negative value
    cpu.status.negative = bool(result & 0x80)

    # Result is only 8 bit, must modulo it to fit register
    cpu.accumulator = result % MAX_UNSIGNED_VALUE

    # Check if the entire register is zero. Or just use int comparison
    cpu.status.zero = cpu.accumulator == 0
