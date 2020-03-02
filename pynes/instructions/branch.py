from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pynes.cpu import Cpu


def branch_if_carry_clear(cpu: 'Cpu', value: int) -> None:
    """BCC instruction"""
    _branch(cpu, not cpu.status.carry, value)


def branch_if_carry_set(cpu: 'Cpu', value: int) -> None:
    """BCS instruction"""
    _branch(cpu, cpu.status.carry, value)


def branch_if_equal(cpu: 'Cpu', value: int) -> None:
    """BEQ instruction"""
    _branch(cpu, cpu.status.zero, value)


def branch_if_minus(cpu: 'Cpu', value: int) -> None:
    """BMI instruction"""
    _branch(cpu, cpu.status.negative, value)


def branch_if_not_equal(cpu: 'Cpu', value: int) -> None:
    """BNE instruction"""
    _branch(cpu, not cpu.status.zero, value)


def branch_if_positive(cpu: 'Cpu', value: int) -> None:
    """BPL instruction"""
    _branch(cpu, not cpu.status.negative, value)


def branch_if_overflow_clear(cpu: 'Cpu', value: int) -> None:
    """BVC instruction"""
    _branch(cpu, not cpu.status.overflow, value)


def branch_if_overflow_set(cpu: 'Cpu', value: int) -> None:
    """BVS instruction"""
    _branch(cpu, cpu.status.overflow, value)


def _branch(cpu: 'Cpu', predicate_for_branch: bool, value: int) -> None:
    if predicate_for_branch:
        cpu.program_counter += value
