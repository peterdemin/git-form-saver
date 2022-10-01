import enum
from typing import List, Tuple


class Formatter(enum.Enum):
    PLAIN_TEXT = enum.auto()
    JSON = enum.auto()


class FormatterInterface:
    def __call__(self, form: List[Tuple[str, str]]) -> str:
        raise NotImplementedError()
