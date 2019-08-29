# pylint: disable=no-self-use
from unittest import mock

import pytest

from pynes import cpu
from testing.util import named_parametrize


class TestAddWithCarryImmediate:
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [
            ('Immediate value', 0, 10, 10),
            ('Accumulator set', 5, 0, 5),
            ('Accumulator set and immediate value', 5, 10, 15),
            ('Upper bound test', 200, 55, 255),
        ],
    )
    def test_adding(self, accumulator_state, immediate, expected):
        """Test basic adding functionality between accumulator and immediate value."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

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
    def test_carry(self, accumulator_state, immediate, expected):
        """Test that carry bit is set when add operation overflows."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

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
    def test_overflow(self, accumulator_state, immediate, expected):
        """Test that overflow bit is set when add operation overflows.

        This is only meaningful if the inputs were intended to be signed values."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.overflow == expected

    @named_parametrize(
        ('accumulator_state', 'immediate'), [('All zero values', 0, 0), ('Result is 256 (overflow)', 200, 56)]
    )
    def test_zero_flag(self, accumulator_state, immediate):
        """Test that result is zero."""
        assert (
            accumulator_state + immediate
        ) % cpu.MAX_UNSIGNED_VALUE == 0, 'Test code assertion, test inputs must only for result == 0'

        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.zero

    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Zero', 0, 0, False), ('Postive', 1, 1, False), ('Negative', 0xFF, 0xFF, True)],
    )
    def test_negative_flag(self, accumulator_state, immediate, expected):
        """Test that negative bit is set if the result is negative."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.negative == expected

    @named_parametrize(
        ('accumulator_state', 'immediate'),
        [('Postiive values', 100, 100), ('Positive overflow', 200, 200), ('Zero', 0, 0)],
    )
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, accumulator_state, immediate, flag_state):
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

    def test_absolute(self):
        """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(test_cpu, '_add_with_carry_immediate') as mock_add:
            test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        mock_add.assert_called_with(5), 'Memory is not accessed in the right place.'

    def test_zero_page(self):
        """Test that zero page addressing is alias for absolute addressing."""
        test_cpu = cpu.Cpu()

        with mock.patch.object(test_cpu, '_add_with_carry_absolute') as mock_add:
            test_cpu.add_with_carry(cpu.AddressingMode.zero_page, 2)

        assert mock_add.called, 'zero_page addressing mode should be identical to absolute mode'


class TestAnd:
    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Match', 0xFF, 0x80, 0x80), ('No match', 0x00, 0x80, 0x00), ('Negative', 0xDD, 0xF0, 0xD0)],
    )
    def test_immediate(self, accumulator_state, immediate, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.accumulator == expected

    def test_absolute(self):
        """Test that absolute addressing gets the value from memory, then performs same addition as immediate."""
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        with mock.patch.object(test_cpu, '_and_immediate') as mock_and:
            test_cpu._and(cpu.AddressingMode.absolute, 2)

        mock_and.assert_called_with(5), 'Memory is not accessed in the right place.'

    @named_parametrize(
        ('accumulator_state', 'immediate', 'expected'),
        [('Some matching values', 0x0F, 0x02, False), ('No matching values', 0xF0, 0x02, True)],
    )
    def test_zero_flag(self, accumulator_state, immediate, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state
        test_cpu._and(cpu.AddressingMode.immediate, immediate)

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

        test_cpu.add_with_carry(cpu.AddressingMode.immediate, immediate)

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

        test_cpu._and(cpu.AddressingMode.immediate, immediate)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state

    def test_zero_page(self):
        """Test that zero page addressing is alias for absolute addressing."""
        test_cpu = cpu.Cpu()

        with mock.patch.object(test_cpu, '_and_absolute') as mock_and:
            test_cpu._and(cpu.AddressingMode.zero_page, 2)

        assert mock_and.called, 'zero_page addressing mode should be identical to absolute mode'


class TestAsl:
    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, 0x0), ('Max', 0xFF, 0xFE), ('Random', 0x11, 0x22)]
    )
    def test_asl(self, accumulator_state, expected):
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.accumulator == expected

    @named_parametrize(('accumulator_state', 'expected'), [('No overflow', 0x0F, False), ('Overflow', 0xFF, True)])
    def test_carry_flag(self, accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.status.carry == expected

    @named_parametrize(
        ('accumulator_state', 'expected'), [('Zero', 0x0, True), ('Non-zero', 0xFF, False), ('0x80', 0x80, True)]
    )
    def test_zero_flag(self, accumulator_state, expected):
        """Test that result is zero."""
        test_cpu = cpu.Cpu()
        test_cpu.accumulator = accumulator_state

        test_cpu.asl(cpu.AddressingMode.accumulator)

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

        test_cpu.asl(cpu.AddressingMode.accumulator)

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

        test_cpu.asl(cpu.AddressingMode.accumulator)

        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state


class TestBranch:
    """Test branching instructions

    Branching instructions differ only with predicate, the rest of code is very similar.
    """

    @staticmethod
    @pytest.fixture
    def test_cpu():
        test_cpu = cpu.Cpu()
        test_cpu.program_counter = 100
        test_cpu.status.carry = False

        yield test_cpu

    @staticmethod
    @pytest.fixture
    def branch():
        """Mock out _branch, this is tested by TestBranch."""
        with mock.patch.object(cpu.Cpu, '_branch') as branch:
            yield branch

    @pytest.mark.parametrize('predicate', [True, False])
    def test_branch(self, test_cpu, predicate):
        test_cpu._branch(predicate, 10)

        assert (test_cpu.program_counter == 110) == predicate

    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, test_cpu, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        test_cpu.program_counter = 100

        test_cpu.status.carry = flag_state
        test_cpu.status.zero = flag_state
        test_cpu.status.interrupt_disable = flag_state
        test_cpu.status.decimal = flag_state
        test_cpu.status.break_ = flag_state
        test_cpu.status.overflow = flag_state
        test_cpu.status.negative = flag_state

        test_cpu._branch(flag_state, 10)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.zero == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state
        assert test_cpu.status.negative == flag_state

    @pytest.mark.parametrize('carry_flag', [True, False])
    def test_branch_if_carry_clear(self, test_cpu, branch, carry_flag):
        """Branch if carry flag is not set (opposite boolean)."""
        test_cpu.status.carry = carry_flag

        test_cpu.branch_if_carry_clear(10)

        branch.assert_called_with(not carry_flag, 10)

    @pytest.mark.parametrize('carry_flag', [True, False])
    def test_branch_if_carry_set(self, test_cpu, branch, carry_flag):
        """Branch if carry flag is set."""
        test_cpu.status.carry = carry_flag

        test_cpu.branch_if_carry_set(10)

        branch.assert_called_with(carry_flag, 10)

    @pytest.mark.parametrize('zero_flag', [True, False])
    def test_branch_if_equal(self, test_cpu, branch, zero_flag):
        """Branch if zero flag is set."""
        test_cpu.status.zero = zero_flag

        test_cpu.branch_if_equal(10)

        branch.assert_called_with(zero_flag, 10)

    @pytest.mark.parametrize('negative_flag', [True, False])
    def test_branch_if_minus(self, test_cpu, branch, negative_flag):
        """Branch if negative flag is set."""
        test_cpu.status.negative = negative_flag

        test_cpu.branch_if_minus(10)

        branch.assert_called_with(negative_flag, 10)

    @pytest.mark.parametrize('zero_flag', [True, False])
    def test_branch_if_not_equal(self, test_cpu, branch, zero_flag):
        """Branch if zero flag is unset."""
        test_cpu.status.zero = zero_flag

        test_cpu.branch_if_not_equal(10)

        branch.assert_called_with(not zero_flag, 10)

    @pytest.mark.parametrize('negative_flag', [True, False])
    def test_branch_if_positive(self, test_cpu, branch, negative_flag):
        """Branch if negative flag is unset."""
        test_cpu.status.negative = negative_flag

        test_cpu.branch_if_positive(10)

        branch.assert_called_with(not negative_flag, 10)

    @pytest.mark.parametrize('overflow_flag', [True, False])
    def test_branch_if_overflow_clear(self, test_cpu, branch, overflow_flag):
        """Branch if overflow flag is unset."""
        test_cpu.status.overflow = overflow_flag

        test_cpu.branch_if_overflow_clear(10)

        branch.assert_called_with(not overflow_flag, 10)

    @pytest.mark.parametrize('overflow_flag', [True, False])
    def test_branch_if_overflow_set(self, test_cpu, branch, overflow_flag):
        """Branch if overflow flag is set."""
        test_cpu.status.overflow = overflow_flag

        test_cpu.branch_if_overflow_set(10)

        branch.assert_called_with(overflow_flag, 10)


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

        test_cpu.bit(2)

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

        test_cpu.bit(2)

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

        test_cpu.bit(2)

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

        test_cpu.bit(2)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state


class TestClear:
    @pytest.mark.parametrize(
        'status_flag',
        (cpu.StatusFlag.carry, cpu.StatusFlag.interrupt_disable, cpu.StatusFlag.decimal, cpu.StatusFlag.overflow),
    )
    @pytest.mark.parametrize('init_state', [True, False])
    def test_clear(self, status_flag, init_state):
        """Test that status flags are always set to false when clear instruction is called."""
        test_cpu = cpu.Cpu()
        setattr(test_cpu.status, status_flag.name, init_state)

        test_cpu._clear_flag(status_flag)

        assert not getattr(test_cpu.status, status_flag.name)

    @pytest.mark.parametrize('status_flag', (cpu.StatusFlag.zero, cpu.StatusFlag.break_, cpu.StatusFlag.negative))
    def test_unsupported_flags(self, status_flag):
        """Test that these statuses do not have clear instruction support."""
        test_cpu = cpu.Cpu()

        with pytest.raises(NotImplementedError):
            test_cpu._clear_flag(status_flag)

    @pytest.mark.parametrize(
        'status_flag',
        (cpu.StatusFlag.carry, cpu.StatusFlag.interrupt_disable, cpu.StatusFlag.decimal, cpu.StatusFlag.overflow),
    )
    @pytest.mark.parametrize('init_state', [True, False])
    @pytest.mark.parametrize('flag_state', [True, False])
    def test_unaffected_flag(self, status_flag, init_state, flag_state):
        """Test that other flags are unchanged."""
        test_cpu = cpu.Cpu()
        setattr(test_cpu.status, status_flag.name, init_state)

        other_status = set(cpu.StatusFlag) - {status_flag}

        # Set state of target status flags
        for i in other_status:
            setattr(test_cpu.status, i.name, flag_state)

        test_cpu._clear_flag(status_flag)

        # Assert state of target status flags unchanged
        for i in other_status:
            assert getattr(test_cpu.status, i.name) == flag_state

    def test_clear_carry(self):
        test_cpu = cpu.Cpu()
        with mock.patch.object(test_cpu, '_clear_flag') as clear_flag:
            test_cpu.clear_carry()
        clear_flag.assert_called_with(cpu.StatusFlag.carry)

    def test_clear_decimal(self):
        test_cpu = cpu.Cpu()
        with mock.patch.object(test_cpu, '_clear_flag') as clear_flag:
            test_cpu.clear_decimal()
        clear_flag.assert_called_with(cpu.StatusFlag.decimal)

    def test_clear_interrupt(self):
        test_cpu = cpu.Cpu()
        with mock.patch.object(test_cpu, '_clear_flag') as clear_flag:
            test_cpu.clear_interrupt()
        clear_flag.assert_called_with(cpu.StatusFlag.interrupt_disable)

    def test_clear_overflow(self):
        test_cpu = cpu.Cpu()
        with mock.patch.object(test_cpu, '_clear_flag') as clear_flag:
            test_cpu.clear_overflow()
        clear_flag.assert_called_with(cpu.StatusFlag.overflow)


class TestCompare:
    @pytest.fixture(autouse=True)
    def test_cpu(self):
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

        yield test_cpu

    def test_negative(self, test_cpu):
        test_cpu._compare(1, 2)

        assert not test_cpu.status.carry
        assert not test_cpu.status.zero
        assert test_cpu.status.negative

    def test_zero(self, test_cpu):
        test_cpu._compare(5, 2)

        assert not test_cpu.status.carry
        assert test_cpu.status.zero
        assert not test_cpu.status.negative

    def test_carry(self, test_cpu):
        test_cpu._compare(10, 2)

        assert test_cpu.status.carry
        assert not test_cpu.status.zero
        assert not test_cpu.status.negative

    def test_cmp(self, test_cpu):
        test_cpu.accumulator = mock.sentinel.accumulator

        with mock.patch.object(cpu.Cpu, '_compare') as compare:
            test_cpu.cmp(2)
        compare.assert_called_with(mock.sentinel.accumulator, 2)

    def test_cpx(self, test_cpu):
        test_cpu.register_x = mock.sentinel.register_x

        with mock.patch.object(cpu.Cpu, '_compare') as compare:
            test_cpu.cpx(2)
        compare.assert_called_with(mock.sentinel.register_x, 2)

    def test_cpy(self, test_cpu):
        test_cpu.register_y = mock.sentinel.register_y

        with mock.patch.object(cpu.Cpu, '_compare') as compare:
            test_cpu.cpy(2)
        compare.assert_called_with(mock.sentinel.register_y, 2)
