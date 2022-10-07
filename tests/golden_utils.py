import pytest


def load_test_cases(test_cases):
    keys = list({key for case in test_cases for key in case})
    return pytest.mark.parametrize(
        ','.join(keys), [tuple(case[k] for k in keys) for case in test_cases]
    )


def assert_golden(name: str, expected: dict, result: dict) -> None:
    del name
    assert result == expected, repr(result)
