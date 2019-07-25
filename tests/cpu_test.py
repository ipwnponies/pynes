from pynes import cpu


class TestAddWithCarryImmediate:
    @staticmethod
    def test_immediate():
        test_cpu = cpu.Cpu()
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, 10)

        assert test_cpu.accumulator == 10


class TestAddWithCarryAbsolute:
    @staticmethod
    def test_absolute():
        test_cpu = cpu.Cpu()
        test_cpu.memory = bytearray(b'\x00\x00\x05\x00')
        test_cpu.add_with_carry(cpu.AddressingMode.absolute, 2)

        assert test_cpu.accumulator == 5
