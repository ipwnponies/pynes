# pylint: disable=no-self-use
from pynes import cpu


class TestDecodeInstruction:
    """decode_instruction is currently a stub."""

    def test_not_placeholder(self):
        cpu_instance = cpu.Cpu()
        cpu_instance.decode_instruction('NOT_PLACEHOLDER')  # type: ignore

    def test_placeholder(self):
        cpu_instance = cpu.Cpu()
        cpu_instance.decode_instruction('PLACEHOLDER')  # type: ignore
