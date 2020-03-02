# pylint: disable=no-self-use
from unittest import mock

import pytest

from pynes import cpu
from pynes.instructions import branch


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
    def branch_():
        """Mock out _branch, this is tested by TestBranch."""
        with mock.patch.object(branch, '_branch') as branch_:
            yield branch_

    @pytest.mark.parametrize('predicate', [True, False])
    def test_branch(self, test_cpu, predicate):
        branch._branch(test_cpu, predicate, 10)

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

        branch._branch(test_cpu, flag_state, 10)

        assert test_cpu.status.carry == flag_state
        assert test_cpu.status.zero == flag_state
        assert test_cpu.status.interrupt_disable == flag_state
        assert test_cpu.status.decimal == flag_state
        assert test_cpu.status.break_ == flag_state
        assert test_cpu.status.overflow == flag_state
        assert test_cpu.status.negative == flag_state

    @pytest.mark.parametrize('carry_flag', [True, False])
    def test_branch_if_carry_clear(self, test_cpu, branch_, carry_flag):
        """Branch if carry flag is not set (opposite boolean)."""
        test_cpu.status.carry = carry_flag

        branch.branch_if_carry_clear(test_cpu, 10)

        branch_.assert_called_with(test_cpu, not carry_flag, 10)

    @pytest.mark.parametrize('carry_flag', [True, False])
    def test_branch_if_carry_set(self, test_cpu, branch_, carry_flag):
        """Branch if carry flag is set."""
        test_cpu.status.carry = carry_flag

        branch.branch_if_carry_set(test_cpu, 10)

        branch_.assert_called_with(test_cpu, carry_flag, 10)

    @pytest.mark.parametrize('zero_flag', [True, False])
    def test_branch_if_equal(self, test_cpu, branch_, zero_flag):
        """Branch if zero flag is set."""
        test_cpu.status.zero = zero_flag

        branch.branch_if_equal(test_cpu, 10)

        branch_.assert_called_with(test_cpu, zero_flag, 10)

    @pytest.mark.parametrize('negative_flag', [True, False])
    def test_branch_if_minus(self, test_cpu, branch_, negative_flag):
        """Branch if negative flag is set."""
        test_cpu.status.negative = negative_flag

        branch.branch_if_minus(test_cpu, 10)

        branch_.assert_called_with(test_cpu, negative_flag, 10)

    @pytest.mark.parametrize('zero_flag', [True, False])
    def test_branch_if_not_equal(self, test_cpu, branch_, zero_flag):
        """Branch if zero flag is unset."""
        test_cpu.status.zero = zero_flag

        branch.branch_if_not_equal(test_cpu, 10)

        branch_.assert_called_with(test_cpu, not zero_flag, 10)

    @pytest.mark.parametrize('negative_flag', [True, False])
    def test_branch_if_positive(self, test_cpu, branch_, negative_flag):
        """Branch if negative flag is unset."""
        test_cpu.status.negative = negative_flag

        branch.branch_if_positive(test_cpu, 10)

        branch_.assert_called_with(test_cpu, not negative_flag, 10)

    @pytest.mark.parametrize('overflow_flag', [True, False])
    def test_branch_if_overflow_clear(self, test_cpu, branch_, overflow_flag):
        """Branch if overflow flag is unset."""
        test_cpu.status.overflow = overflow_flag

        branch.branch_if_overflow_clear(test_cpu, 10)

        branch_.assert_called_with(test_cpu, not overflow_flag, 10)

    @pytest.mark.parametrize('overflow_flag', [True, False])
    def test_branch_if_overflow_set(self, test_cpu, branch_, overflow_flag):
        """Branch if overflow flag is set."""
        test_cpu.status.overflow = overflow_flag

        branch.branch_if_overflow_set(test_cpu, 10)

        branch_.assert_called_with(test_cpu, overflow_flag, 10)
