# pylint: disable=no-self-use
from unittest import mock

import pytest

from pynes import cpu


class TestDecodeInstruction:
    """decode_instruction is currently a stub."""

    def test_not_placeholder(self):
        cpu_instance = cpu.Cpu()
        cpu_instance.decode_instruction('NOT_PLACEHOLDER')  # type: ignore

    def test_placeholder(self):
        cpu_instance = cpu.Cpu()
        cpu_instance.decode_instruction('PLACEHOLDER')  # type: ignore


# TODO: Move all the following opcode test cases to separate modules


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
