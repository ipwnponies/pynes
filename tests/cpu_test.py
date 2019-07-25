from pynes import cpu


class TestAddWithCarry:
    @staticmethod
    def test_add_with_carry():
        test_cpu = cpu.Cpu()
        test_cpu.add_with_carry(cpu.AddressingMode.immediate, 10)

        assert test_cpu.accumulator == 10
