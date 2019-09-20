import enum


class AddressingMode(enum.Enum):
    immediate = enum.auto()
    absolute = enum.auto()
    zero_page = enum.auto()
    accumulator = enum.auto()
