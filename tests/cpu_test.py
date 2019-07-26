from unittest import mock

import pytest

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
            ('Upper bound test', 200, 55, 255),
        ],
    )
    def test_adding(accumulator_state, immediate, expected):
        """Test basic adding functionality between accumulator and immediate value."""
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
        """Test that overflow bit is set when add operation overflows.

        This is only meaningful if the inputs were intended to be signed values."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_overflow == expected

    @staticmethod
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
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_zero

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Zero', 0, 0, False), ('Postive', 1, 1, False), ('Negative', 0xFF, 0xFF, True)],
    )
    def test_negative_flag(accumulator_state, immediate, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_negative == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate'),
        [('Postiive values', 100, 100), ('Positive overflow', 200, 200), ('Zero', 0, 0)],
    )
    @pytest.mark.parametrize(('flag_state'), [(True,), (False,)])
    def test_unaffected_flag(accumulator_state, immediate, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.processor_status_interrupt_disable = flag_state
        test_cpu.processor_status_decimal_mode = flag_state
        test_cpu.processor_status_break_command = flag_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_interrupt_disable == flag_state
        assert test_cpu.processor_status_decimal_mode == flag_state
        assert test_cpu.processor_status_break_command == flag_state

    @staticmethod
    def test_absolute():
        """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(test_cpu, '_add_with_carry_immediate') as mock_add:
            test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert mock_add.called_with(5), 'Memory is not accessed in the right place.'

    @staticmethod
    def test_zero_page():
        """Test that zero page addressing is alias for absolute addressing."""
        test_cpu = cpu.Cpu()

        with mock.patch.object(test_cpu, '_add_with_carry_absolute') as mock_add:
            test_cpu.add_with_carry(cpu.AddressingMode.zero_page, 2)

        assert mock_add.called, 'zero_page addressing mode should be identical to absolute mode'


class TestAnd:
    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Match', 0xFF, 0x80, 0x80), ('No match', 0x00, 0x80, 0x00), ('Negative', 0xDD, 0xF0, 0xD0)],
    )
    def test_immediate(accumulator_state, immediate, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.accumulator == expected

    @staticmethod
    def test_absolute():
        """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(test_cpu, '_and_immediate') as mock_and:
            test_cpu._and(cpu.AddressingMode.absolute, 2)

        assert mock_and.called_with(5), 'Memory is not accessed in the right place.'

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Some matching values', 0x0F, 0x02, False), ('No matching values', 0xF0, 0x02, True)],
    )
    def test_zero_flag(accumulator_state, immediate, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_zero == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [
            ('Both positive', 0x0F, 0x0F, False),
            ('Mixed1', 0xF0, 0x70, False),
            ('Mixed2', 0x70, 0xF0, False),
            ('both negative', 0xF0, 0xF0, True),
        ],
    )
    def test_negative_flag(accumulator_state, immediate, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_negative == expected

    @staticmethod
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
    @pytest.mark.parametrize(('flag_state'), [(True,), (False,)])
    def test_unaffected_flag(accumulator_state, immediate, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.processor_status_carry = flag_state
        test_cpu.processor_status_interrupt_disable = flag_state
        test_cpu.processor_status_decimal_mode = flag_state
        test_cpu.processor_status_break_command = flag_state
        test_cpu.processor_status_overflow = flag_state

        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.processor_status_carry == flag_state
        assert test_cpu.processor_status_interrupt_disable == flag_state
        assert test_cpu.processor_status_decimal_mode == flag_state
        assert test_cpu.processor_status_break_command == flag_state
        assert test_cpu.processor_status_overflow == flag_state

    @staticmethod
    def test_zero_page():
        """Test that zero page addressing is alias for absolute addressing."""
        test_cpu = cpu.Cpu()

        with mock.patch.object(test_cpu, '_and_absolute') as mock_and:
            test_cpu._and(cpu.AddressingMode.zero_page, 2)

        assert mock_and.called, 'zero_page addressing mode should be identical to absolute mode'


class TestAsl:
    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)]
    )
    def test_asl(accumulator_state, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.accumulator == expected

    @staticmethod
    @named_parametrize(('accumulator_state', 'expected'), [('No overflow', 0x0F, False), ('Overflow', 0xFF, True)])
    def test_carry_flag(accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.processor_status_carry == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, True), ('Non-zero', 0xFF, False), ('0x80', 0x80, True)]
    )
    def test_zero_flag(accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.processor_status_zero == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'expected'),
        [
            ('Positive->Positive', 0x0F, False),
            ('Positive->Negative', 0x70, True),
            ('Negative->Negative', 0xF0, True),
            ('Negative->Positive', 0x81, False),
        ],
    )
    def test_negative_flag(accumulator_state, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.processor_status_negative == expected

    @staticmethod
    @named_parametrize(('accumulator_state'), [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)])
    @pytest.mark.parametrize(('flag_state'), [(True,), (False,)])
    def test_unaffected_flag(accumulator_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.processor_status_interrupt_disable = flag_state
        test_cpu.processor_status_decimal_mode = flag_state
        test_cpu.processor_status_break_command = flag_state
        test_cpu.processor_status_overflow = flag_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.processor_status_interrupt_disable == flag_state
        assert test_cpu.processor_status_decimal_mode == flag_state
        assert test_cpu.processor_status_break_command == flag_state
        assert test_cpu.processor_status_overflow == flag_state
