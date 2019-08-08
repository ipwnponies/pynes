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
        assert not test_cpu.status.carry

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

        assert test_cpu.status.carry == expected

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

        assert test_cpu.status.overflow == expected

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

        assert test_cpu.status.zero

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

        assert test_cpu.status.negative == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'immediate'),
        [('Postiive values', 100, 100), ('Positive overflow', 200, 200), ('Zero', 0, 0)],
    )
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(accumulator_state, immediate, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state

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

        assert test_cpu.status.zero == expected

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

        assert test_cpu.status.negative == expected

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
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(accumulator_state, immediate, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.status.carry = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state

        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state

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

        assert test_cpu.status.carry == expected

    @staticmethod
    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, True), ('Non-zero', 0xFF, False), ('0x80', 0x80, True)]
    )
    def test_zero_flag(accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.status.zero == expected

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

        assert test_cpu.status.negative == expected

    @staticmethod
    @named_parametrize('accumulator_state', [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)])
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(accumulator_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state


class TestBranchIfCarryClear:
    @staticmethod
    def test():
        test_cpu = cpu.Cpu()
        test_cpu.program_counter = 100
        test_cpu.status.carry = False

        test_cpu.branch_if_carry_clear(10)

        assert test_cpu.program_counter == 110

    @staticmethod
    def test_carry_set():
        test_cpu = cpu.Cpu()
        test_cpu.program_counter = 100
        test_cpu.status.carry = True

        test_cpu.branch_if_carry_clear(10)

        assert test_cpu.program_counter == 100

    @staticmethod
    @pytest.mark.parametrize('carry_state', [True, False])
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(carry_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.program_counter = 100
        test_cpu.status.carry = carry_state

        test_cpu.status.zero = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state
        test_cpu.status.negative = flag_state

        test_cpu.branch_if_carry_clear(10)

        assert test_cpu.status.carry == carry_state
        assert test_cpu.status.zero == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state
        assert test_cpu.status.negative == flag_state


class TestClear:
    @staticmethod
    @pytest.mark.parametrize(
        'status_flag',
        (cpu.StatusFlag.carry, cpu.StatusFlag.interrupt_disable, cpu.StatusFlag.decimal, cpu.StatusFlag.overflow),
    )
    @pytest.mark.parametrize('init_carry_state', [True, False])
    def test_clear(status_flag, init_carry_state):
        """Test that carry flag is always set to false."""
        test_cpu = cpu.Cpu()
        test_cpu.status.carry = init_carry_state

        test_cpu.clear_carry()

        assert not test_cpu.status.carry

    @staticmethod
    @pytest.mark.parametrize('status_flag', (cpu.StatusFlag.zero, cpu.StatusFlag.break_, cpu.StatusFlag.negative))
    @pytest.mark.parametrize('init_state', [True, False])
    def test_unsupported_flags(status_flag, init_state):
        """Test that these statuses do not have clear instruction support."""
        test_cpu = cpu.Cpu()
        test_cpu.status.zero = init_state

        with pytest.raises(NotImplementedError):
            test_cpu._clear_flag(status_flag)

    @pytest.mark.skip
    @staticmethod
    @pytest.mark.parametrize('init_carry_state', [True, False])
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(status_flag, init_carry_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.status.carry = init_carry_state

        test_cpu.status.zero = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state
        test_cpu.status.negative = flag_state

        test_cpu.clear_carry()

        assert test_cpu.status.zero == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state
        assert test_cpu.status.negative == flag_state
