from unittest import mock

from pynes import cpu
from testing.util import named_parametrize


class TestAddWithCarryImmediate:
    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [
            ('Immediate value', 0, 10, 10),
            ('Accumulator set', 5, 0, 5),
            ('Accumulator set and immediate value', 5, 10, 15),
        ],
    )
    def test_adding(accumulator_state, immediate, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.accumulator == expected
        assert not test_cpu.processor_status_carry

    @staticmethod
    def test_overflow():
        """Test that carry bit is set when add operation overflows."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = 10
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, 8)

        assert test_cpu.accumulator == 2
        assert test_cpu.processor_status_carry

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate'), [('All zero values', 0, 0), ('Result is 16 (overflow)', 10, 6)]
    )
    def test_zero_flag(accumulator_state, immediate):
        assert (accumulator_state + immediate) % 16 == 0, 'Test code assertion, test inputs must only for result == 0'

        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_zero


class TestAddWithCarryAbsolute:
    """After memory address is accessed, this operation is identical to adding in immediate addressing."""

    @staticmethod
    def test_absolute():
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(test_cpu, '_add_with_carry_immediate') as mock_add:
            test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert mock_add.called_with(5), 'Memory is not accessed in the right place.'
