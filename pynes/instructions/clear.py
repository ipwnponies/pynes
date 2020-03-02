from typing import TYPE_CHECKING

from pynes.cpu import StatusFlag

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def clear_carry(cpu: 'Cpu') -> None:
    _clear_flag(cpu, StatusFlag.carry)


def clear_decimal(cpu: 'Cpu') -> None:
    _clear_flag(cpu, StatusFlag.decimal)


def clear_interrupt(cpu: 'Cpu') -> None:
    _clear_flag(cpu, StatusFlag.interrupt_disable)


def clear_overflow(cpu: 'Cpu') -> None:
    _clear_flag(cpu, StatusFlag.overflow)


def _clear_flag(cpu: 'Cpu', flag: StatusFlag) -> None:
    """Clear carry status flag."""
    if flag == StatusFlag.carry:
        cpu.status.carry = False
    elif flag == StatusFlag.decimal:
        cpu.status.decimal = False
    elif flag == StatusFlag.interrupt_disable:
        cpu.status.interrupt_disable = False
    elif flag == StatusFlag.overflow:
        cpu.status.overflow = False
    else:
        raise NotImplementedError(f'{flag} mode is not supported')
