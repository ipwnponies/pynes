from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def bit(cpu: 'Cpu', value: int) -> None:
    """Bitmask operation

    Bitmask pattern is located in accumulator and memory value is target.
    This is really an AND operation, for bitmasking purposes."""
    arg1 = cpu.accumulator
    arg2 = cpu.read_from_memory(value)

    # Set zero flag if bitmask masks everything
    cpu.status.zero = not arg1 & arg2
    cpu.status.negative = bool(1 << 7 & arg2)
    cpu.status.overflow = bool(1 << 6 & arg2)
