from typing import TYPE_CHECKING

MAX_UNSIGNED_VALUE = 2 ** 8

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def cmp(cpu: 'Cpu', value: int) -> None:
    _compare(cpu, cpu.accumulator, value)


def cpx(cpu: 'Cpu', value: int) -> None:
    _compare(cpu, cpu.register_x, value)


def cpy(cpu: 'Cpu', value: int) -> None:
    _compare(cpu, cpu.register_y, value)


def _compare(cpu: 'Cpu', arg1: int, value: int) -> None:
    """Compare accumulator against memory value."""
    arg2 = cpu.read_from_memory(value)

    result = arg1 - arg2

    cpu.status.carry = result > 0
    cpu.status.zero = result == 0
    cpu.status.negative = result < 0
