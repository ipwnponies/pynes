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
