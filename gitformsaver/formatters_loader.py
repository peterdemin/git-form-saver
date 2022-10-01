from typing import Dict
from .formatters import Formatter
from .plain_text_formatter import PlainTextFormatter
from .json_formatter import JSONFormatter
from .formatters import FormatterInterface


def load_formatters() -> Dict[Formatter, FormatterInterface]:
    return {
        Formatter.PLAIN_TEXT: PlainTextFormatter(),
        Formatter.JSON: JSONFormatter(),
    }
