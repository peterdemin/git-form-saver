from typing import List, Tuple


class FormFormatter:
    def __call__(self, form: List[Tuple[str, str]]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in form)
