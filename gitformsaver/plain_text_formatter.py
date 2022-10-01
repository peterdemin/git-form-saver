from typing import List, Tuple
from .formatters import FormatterInterface


class PlainTextFormatter(FormatterInterface):
    def __call__(self, form: List[Tuple[str, str]]) -> str:
        content = "".join(f"{key}: {value}\n" for key, value in form)
        if content:
            return content + "\n"
        return ''
