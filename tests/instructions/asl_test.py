# pylint: disable=no-self-use
import pytest

from pynes import cpu
from pynes.instructions.asl import asl
from testing.util import named_parametrize


class TestAsl:
    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)]
    )
    def test_asl(self, accumulator_state, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        asl(test_cpu, cpu.AddressingMode.accumulator)

        assert test_cpu.accumulator == expected

    @named_parametrize(('accumulator_state', 'expected'), [('No overflow', 0x0F, False), ('Overflow', 0xFF, True)])
    def test_carry_flag(self, accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        asl(test_cpu, cpu.AddressingMode.accumulator)

        assert test_cpu.status.carry == expected

    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, True), ('Non-zero', 0xFF, False), ('0x80', 0x80, True)]
    )
    def test_zero_flag(self, accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        asl(test_cpu, cpu.AddressingMode.accumulator)

        assert test_cpu.status.zero == expected

    @named_parametrize(
        ('accumulator_state', 'expected'),
        [
            ('Positive->Positive', 0x0F, False),
            ('Positive->Negative', 0x70, True),
            ('Negative->Negative', 0xF0, True),
            ('Negative->Positive', 0x81, False),
        ],
    )
    def test_negative_flag(self, accumulator_state, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        asl(test_cpu, cpu.AddressingMode.accumulator)

        assert test_cpu.status.negative == expected

    @named_parametrize('accumulator_state', [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)])
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, accumulator_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state

        asl(test_cpu, cpu.AddressingMode.accumulator)

        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state
