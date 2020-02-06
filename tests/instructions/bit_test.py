# pylint: disable=no-self-use
import pytest

from pynes import cpu
from pynes.instructions import bit
from testing.util import named_parametrize


class TestBit:
    @named_parametrize(
        ('accumulator_state', 'memory_value', 'expected'),
        [('No match', 0x00, 0xFF, True), ('All match', 0xFF, 0xFF, False), ('Some match', 0x0F, 0x04, False)],
    )
    def test_zero(self, accumulator_state, memory_value, expected):
        """Test that zero flag is only set if bitmasking is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.memory = bytearray(10)
        test_cpu.memory[2] = memory_value

        bit.bit(test_cpu, 2)

        assert test_cpu.status.zero == expected

    @named_parametrize(
        ('accumulator_state', 'memory_value', 'expected'),
        [
            ('Memory value bit set', 0x0, 0x40, True),
            ('Memory value bit not set', 0x0, 0b10111111, False),
            ('Memory value bit set even if zero set (bitmask)', 0xFF, 0x40, True),
        ],
    )
    def test_overflow(self, accumulator_state, memory_value, expected):
        """Test that overflow is set to 6th bit of memory value."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.memory = bytearray(10)
        test_cpu.memory[2] = memory_value

        bit.bit(test_cpu, 2)

        assert test_cpu.status.overflow == expected

    @named_parametrize(
        ('accumulator_state', 'memory_value', 'expected'),
        [
            ('Memory value bit set', 0x0, 0x80, True),
            ('Memory value bit not set', 0x0, 0b01111111, False),
            ('Memory value bit set even if zero set (bitmask)', 0xFF, 0x80, True),
        ],
    )
    def test_negative(self, accumulator_state, memory_value, expected):
        """Test that negative is set to 7th bit of memory value."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.memory = bytearray(10)
        test_cpu.memory[2] = memory_value

        bit.bit(test_cpu, 2)

        assert test_cpu.status.negative == expected

    @named_parametrize(
        ('accumulator_state', 'memory_value'),
        [('No match', 0x00, 0xFF), ('All match', 0xFF, 0xFF), ('Some match', 0x0F, 0x04)],
    )
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, accumulator_state, memory_value, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.memory = bytearray(10)
        test_cpu.memory[2] = memory_value

        test_cpu.status.carry = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state

        bit.bit(test_cpu, 2)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
