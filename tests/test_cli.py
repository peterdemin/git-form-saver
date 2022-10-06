import sys
from gitformsaver.cli import generate_token


def test_can_generate_token() -> None:
    sys.argv.extend(['repo', 'file'])
    generate_token()
