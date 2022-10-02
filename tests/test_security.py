import os

import pytest

from gitformsaver.security import Security

HERE = os.path.abspath(os.path.dirname(__file__))
KEYS_PATH = os.path.join(HERE, "keys")
PRIVATE_KEY_PATH = os.path.join(KEYS_PATH, "id_rsa")


@pytest.mark.parametrize('secret', ['', 'secret'])
def test_signature_is_valid(security: Security, secret: str) -> None:
    signature = security.sign_target(repo='repo', path='path', secret=secret)
    assert signature
    assert len(signature) == 512
    assert security.is_valid(signature, repo='repo', path='path', secret=secret)


@pytest.fixture(name='security')
def _security() -> Security:
    return Security(private_key_path=PRIVATE_KEY_PATH)
