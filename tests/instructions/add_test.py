from unittest import mock

import pytest

from pynes import cpu
from pynes.instructions import add
from testing.util import named_parametrize


@named_parametrize(
    ('accumulator_state', 'immediate', 'expected'),
    [
        ('Immediate value', 0, 10, 10),
        ('Accumulator set', 5, 0, 5),
        ('Accumulator set and immediate value', 5, 10, 15),
        ('Upper bound test', 200, 55, 255),
    ],
)
def test_adding(accumulator_state, immediate, expected):
    """Test basic adding functionality between accumulator and immediate value."""
    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state
    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.accumulator == expected
    assert not test_cpu.status.carry


@named_parametrize(
    ('accumulator_state', 'immediate', 'expected'),
    [
        ('Carry and overflow', 0xF0, 0xF0, True),
        ('Carry but no overflow', 0xFF, 0xFF, True),
        ('No carry or overflow', 0x0F, 0x0F, False),
        ('No carry but has overflow', 0b1000000, 0b1000000, False),
    ],
)
def test_carry(accumulator_state, immediate, expected):
    """Test that carry bit is set when add operation overflows."""
    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state
    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.status.carry == expected


@named_parametrize(
    ('accumulator_state', 'immediate', 'expected'),
    [
        ('Carry and overflow', 0b10000000, 0b10000000, True),
        ('Carry but no overflow', 0xFF, 0xFF, False),
        ('No carry or overflow', 0x01, 0x01, False),
        ('No carry but has overflow', 0b01000000, 0b01000000, True),
    ],
)
def test_overflow(accumulator_state, immediate, expected):
    """Test that overflow bit is set when add operation overflows.

    This is only meaningful if the inputs were intended to be signed values."""
    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state

    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.status.overflow == expected


@named_parametrize(
    ('accumulator_state', 'immediate'), [('All zero values', 0, 0), ('Result is 256 (overflow)', 200, 56)]
)
def test_zero_flag(accumulator_state, immediate):
    """Test that result is zero."""
    assert (
        accumulator_state + immediate
    ) % cpu.MAX_UNSIGNED_VALUE == 0, 'Test code assertion, test inputs must only for result == 0'

    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state
    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.status.zero


@named_parametrize(
    ('accumulator_state', 'immediate', 'expected'),
    [('Zero', 0, 0, False), ('Postive', 1, 1, False), ('Negative', 0xFF, 0xFF, True)],
)
def test_negative_flag(accumulator_state, immediate, expected):
    """Test that negative bit is set if the result is negative."""
    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state

    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.status.negative == expected


@named_parametrize(
    ('accumulator_state', 'immediate'), [('Postiive values', 100, 100), ('Positive overflow', 200, 200), ('Zero', 0, 0)]
)
@pytest.mark.parametrize('flag_state', [True, False])
def test_unaffected_flag(accumulator_state, immediate, flag_state):
    """Test that other flags are unchanged."""
    test_cpu = cpu.Cpu()
    test_cpu.accumulator = accumulator_state

    test_cpu.status.interrupt_disable = flag_state
    test_cpu.status.decimal = flag_state
    test_cpu.status.break_ = flag_state

    add.add_with_carry(test_cpu, cpu.AddressingMode.immediate, immediate)

    assert test_cpu.status.interrupt_disable == flag_state
    assert test_cpu.status.decimal == flag_state
    assert test_cpu.status.break_ == flag_state


def test_absolute():
    """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
    test_cpu = cpu.Cpu()
    test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

    with mock.patch.object(add, '_add_with_carry_immediate', wraps=add._add_with_carry_immediate) as mock_add:
        add.add_with_carry(test_cpu, cpu.AddressingMode.absolute, 2)

    mock_add.assert_called_with(test_cpu, 5), 'Memory is not accessed in the right place.'


def test_zero_page():
    """Test that zero page addressing is alias for absolute addressing."""
    test_cpu = cpu.Cpu()
    test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

    function = add._add_with_carry_absolute
    with mock.patch.object(add, function.__name__, wraps=function) as mock_add:
        add.add_with_carry(test_cpu, cpu.AddressingMode.zero_page, 2)

    assert mock_add.called, 'zero_page addressing mode should be identical to absolute mode'
