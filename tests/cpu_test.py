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
            ('Upper bound test', 100, 27, 127),
        ],
    )
    def test_adding(accumulator_state, immediate, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.accumulator == expected
        assert not test_cpu.processor_status_carry

    @staticmethod
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
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_carry == expected

    @staticmethod
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
        """Test that carry bit is set when add operation overflows."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_overflow == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate'), [('All zero values', 0, 0), ('Result is 128 (overflow)', 100, 28)]
    )
    def test_zero_flag(accumulator_state, immediate):
        assert (accumulator_state + immediate) % (
            2 ** 7
        ) == 0, 'Test code assertion, test inputs must only for result == 0'

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
