import hmac
import os
from functools import cached_property
from typing import Dict, cast

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.ssh import load_ssh_private_key


class Authentication:
    _ALGORITHM = "RS256"
    _HASH_ALGORITHM = "SHA256"

    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path or os.path.expanduser("~/.ssh/id_rsa")

    def create_token(self, repo: str, path: str, secret: str = '') -> str:
        return self._encode(self._format_payload(repo, path, secret))

    def is_valid_token(self, token: str, repo: str, path: str, secret: str = '') -> bool:
        return self._decode(token) == self._format_payload(repo, path, secret)

    def _format_payload(self, repo: str, path: str, secret: str) -> str:
        return {
            self._HASH_ALGORITHM: hmac.new(
                key=(secret or 'secret').encode('utf-8'),
                msg=f'{repo} {path}'.encode('utf-8'),
                digestmod=self._HASH_ALGORITHM.lower(),
            ).hexdigest()
        }

    def _encode(self, payload: Dict[str, str]) -> bytes:
        return jwt.encode(payload=payload, key=self._private_key, algorithm=self._ALGORITHM)

    def _decode(self, token: str) -> Dict[str, str]:
        return jwt.decode(jwt=token, key=self._public_key, algorithms=self._ALGORITHM)

    @cached_property
    def _private_key(self) -> rsa.RSAPrivateKey:
        with open(self._private_key_path, "rb") as fobj:
            # Only RSA supports signing
            return cast(rsa.RSAPrivateKey, load_ssh_private_key(fobj.read(), password=None))

    @cached_property
    def _public_key(self) -> rsa.RSAPublicKey:
        return self._private_key.public_key()
