from unittest import mock

import pytest

from pynes import cpu
from pynes.instructions import and_
from testing.util import named_parametrize


class TestAnd:
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Match', 0xFF, 0x80, 0x80), ('No match', 0x00, 0x80, 0x00), ('Negative', 0xDD, 0xF0, 0xD0)],
    )
    def test_immediate(self, accumulator_state, immediate, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        and_.and_(test_cpu, cpu.AddressingMode.immediate, immediate)

        assert test_cpu.accumulator == expected

    def test_absolute(self):
        """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(and_, 'and_immediate') as mock_and:
            and_.and_(test_cpu, cpu.AddressingMode.absolute, 2)

        mock_and.assert_called_with(test_cpu, 5), 'Memory is not accessed in the right place.'

    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Some matching values', 0x0F, 0x02, False), ('No matching values', 0xF0, 0x02, True)],
    )
    def test_zero_flag(self, accumulator_state, immediate, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        and_.and_(test_cpu, cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.zero == expected

    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [
            ('Both positive', 0x0F, 0x0F, False),
            ('Mixed1', 0xF0, 0x70, False),
            ('Mixed2', 0x70, 0xF0, False),
            ('both negative', 0xF0, 0xF0, True),
        ],
    )
    def test_negative_flag(self, accumulator_state, immediate, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        and_.and_(test_cpu, cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.negative == expected

    @named_parametrize(
        ('accumulator_state', 'immediate'),
        [
            ('Zero', 0x0, 0x0),
            ('Max values', 0xFF, 0xFF),
            ('Both positive', 0x0F, 0x73),
            ('Both negative', 0xF0, 0xD3),
            ('Potential singed overflow', 0b01000000, 0b01000000),
        ],
    )
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, accumulator_state, immediate, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.status.carry = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state

        and_.and_(test_cpu, cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state

    def test_zero_page(self):
        """Test that zero page addressing is alias for absolute addressing."""
        test_cpu = cpu.Cpu()

        with mock.patch.object(and_, 'and_absolute') as mock_and:
            and_.and_(test_cpu, cpu.AddressingMode.zero_page, 2)

        assert mock_and.called, 'zero_page addressing mode should be identical to absolute mode'
