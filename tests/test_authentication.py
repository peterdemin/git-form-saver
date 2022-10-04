import os

import pytest

from gitformsaver.authentication import Authentication

HERE = os.path.abspath(os.path.dirname(__file__))
KEYS_PATH = os.path.join(HERE, "keys")
PRIVATE_KEY_PATH = os.path.join(KEYS_PATH, "id_rsa")


@pytest.mark.parametrize('secret', ['', '***', 'very-long-secret-' * 10])
def test_new_token_is_valid(authentication: Authentication, secret: str) -> None:
    token = authentication.create_token('repo', 'path', secret)
    assert token
    assert authentication.is_valid_token(token, 'repo', 'path', secret)
    assert len(token) == 653


@pytest.fixture(name='authentication')
def _authentication() -> Authentication:
    return Authentication(private_key_path=PRIVATE_KEY_PATH)
