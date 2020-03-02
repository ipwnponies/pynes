# pylint: disable=no-self-use
from unittest import mock

import pytest

from pynes import cpu
from pynes.instructions import cmp


@pytest.fixture
def test_cpu():
    test_cpu = cpu.Cpu()
    test_cpu.memory = bytearray(b'\x00\x00\x05\x00')

    yield test_cpu


@pytest.mark.parametrize(('test_value', 'expected'), [(1, True), (10, False)])
def test_negative(test_cpu, test_value, expected):
    memory_address = 2
    cmp._compare(test_cpu, test_value, memory_address)

    assert test_cpu.status.negative == expected


def test_zero(test_cpu):
    cmp._compare(test_cpu, 5, 2)

    assert not test_cpu.status.carry
    assert test_cpu.status.zero
    assert not test_cpu.status.negative


def test_carry(test_cpu):
    cmp._compare(test_cpu, 10, 2)

    assert test_cpu.status.carry
    assert not test_cpu.status.zero
    assert not test_cpu.status.negative


class TestCompareInstructions:
    def test_cmp(self, test_cpu):
        test_cpu.accumulator = mock.sentinel.accumulator

        with mock.patch.object(cmp, '_compare') as compare:
            cmp.cmp(test_cpu, 2)
        compare.assert_called_with(test_cpu, mock.sentinel.accumulator, 2)

    def test_cpx(self, test_cpu):
        test_cpu.register_x = mock.sentinel.register_x

        with mock.patch.object(cmp, '_compare') as compare:
            cmp.cpx(test_cpu, 2)
        compare.assert_called_with(test_cpu, mock.sentinel.register_x, 2)

    def test_cpy(self, test_cpu):
        test_cpu.register_y = mock.sentinel.register_y

        with mock.patch.object(cmp, '_compare') as compare:
            cmp.cpy(test_cpu, 2)
        compare.assert_called_with(test_cpu, mock.sentinel.register_y, 2)
