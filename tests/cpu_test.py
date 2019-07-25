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
    @staticmethod
    @named_parametrize(('accumulator_state', 'expected'), [('Accumulator unset', 0, 5), ('Accumulator set', 5, 10)])
    def test_absolute(accumulator_state, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        # Intial memory values
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert test_cpu.accumulator == expected
        assert not test_cpu.processor_status_carry

    @staticmethod
    def test_overflow():
        """Test that carry bit is set when add operation overflows."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = 10
        test_cpu.memory = bytearray(b'\x00\x00\x08\x00')

        test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert test_cpu.accumulator == 2
        assert test_cpu.processor_status_carry

    @staticmethod
    @named_parametrize(('accumulator_state', 'value'), [('All zero values', 0, 0), ('Result is 16 (overflow)', 10, 6)])
    def test_zero_flag(accumulator_state, value):
        assert (accumulator_state + value) % 16 == 0, 'Test code assertion, test inputs must only for result == 0'

        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.memory = bytearray(4)
        test_cpu.memory[2] = value
        test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert test_cpu.processor_status_zero
