from typing import List, Tuple
import json
from .formatters import FormatterInterface


class JSONFormatter(FormatterInterface):
    def __call__(self, form: List[Tuple[str, str]]) -> str:
        content = json.dumps(form)
        if content:
            return content + "\n"
        return ''
