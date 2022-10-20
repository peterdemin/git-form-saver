import functools
from typing import Callable


class GoldenTestCase:
    def __init__(self, test_cases: list) -> None:
        self._test_cases = test_cases
        self._keys = list({key for case in test_cases for key in case})

    def __call__(self, cls):
        for test_case in self._test_cases:
            name = test_case.pop('name')
            setattr(cls, f'test_{name}', bind_kwargs(cls, test_produces_expected, test_case))
        return cls


def test_produces_expected(self, parameters, expected):
    assert self.produce(parameters) == expected


def bind_kwargs(cls, unbound_method: Callable, kwargs: dict) -> Callable:
    @functools.wraps(unbound_method)
    def wrapped(self):
        test_method = unbound_method.__get__(self, cls)  # pylint: disable=unnecessary-dunder-call
        test_method(**kwargs)

    return wrapped


golden_test = GoldenTestCase  # pylint: disable=invalid-name
