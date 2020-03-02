# pylint: disable=no-self-use
from unittest import mock

import pytest

from pynes import cpu
from pynes.instructions import clear


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

        clear._clear_flag(test_cpu, status_flag)

        assert not getattr(test_cpu.status, status_flag.name)

    @pytest.mark.parametrize('status_flag', (cpu.StatusFlag.zero, cpu.StatusFlag.break_, cpu.StatusFlag.negative))
    def test_unsupported_flags(self, status_flag):
        """Test that these statuses do not have clear instruction support."""
        test_cpu = cpu.Cpu()

        with pytest.raises(NotImplementedError):
            clear._clear_flag(test_cpu, status_flag)

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

        clear._clear_flag(test_cpu, status_flag)

        # Assert state of target status flags unchanged
        for i in other_status:
            assert getattr(test_cpu.status, i.name) == flag_state


class TestClearOpCode:
    @pytest.fixture
    def mock_clear(self):
        with mock.patch.object(clear, '_clear_flag') as mock_clear:
            yield mock_clear

    def test_clear_carry(self, mock_clear):
        test_cpu = cpu.Cpu()
        clear.clear_carry(test_cpu)
        mock_clear.assert_called_with(test_cpu, cpu.StatusFlag.carry)

    def test_clear_decimal(self, mock_clear):
        test_cpu = cpu.Cpu()
        clear.clear_decimal(test_cpu)
        mock_clear.assert_called_with(test_cpu, cpu.StatusFlag.decimal)

    def test_clear_interrupt(self, mock_clear):
        test_cpu = cpu.Cpu()
        clear.clear_interrupt(test_cpu)
        mock_clear.assert_called_with(test_cpu, cpu.StatusFlag.interrupt_disable)

    def test_clear_overflow(self, mock_clear):
        test_cpu = cpu.Cpu()
        clear.clear_overflow(test_cpu)
        mock_clear.assert_called_with(test_cpu, cpu.StatusFlag.overflow)
