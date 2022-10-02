import os
import base64
from typing import cast
from functools import cached_property

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization.ssh import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes


class Security:
    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path or os.path.expanduser("~/.ssh/id_rsa")

    def sign_target(self, repo: str, path: str, secret: str = '') -> str:
        binary_signature = self._private_key.sign(
            self._compose_message(repo, path, secret),
            padding=self._padding,
            algorithm=self._hashing_algorithm,
        )
        return self._encode(binary_signature)

    def is_valid(self, signature: str, repo: str, path: str, secret: str = '') -> bool:
        try:
            self._public_key.verify(
                self._decode(signature),
                self._compose_message(repo, path, secret),
                padding=self._padding,
                algorithm=self._hashing_algorithm,
            )
        except InvalidSignature:
            return False
        return True

    @cached_property
    def _private_key(self) -> rsa.RSAPrivateKey:
        with open(self._private_key_path, "rb") as fobj:
            # Only RSA supports signing
            return cast(rsa.RSAPrivateKey, load_ssh_private_key(fobj.read(), password=None))

    @cached_property
    def _public_key(self) -> rsa.RSAPublicKey:
        return self._private_key.public_key()

    def _compose_message(self, repo: str, path: str, secret: str) -> bytes:
        return f'{repo} {path}{secret}'.encode('utf-8')

    @property
    def _padding(self) -> padding.AsymmetricPadding:
        return padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )

    @property
    def _hashing_algorithm(self) -> hashes.HashAlgorithm:
        return hashes.SHA256()

    def _encode(self, binary_signature: bytes) -> str:
        return base64.b64encode(binary_signature).decode('ascii')

    def _decode(self, signature: str) -> bytes:
        return base64.b64decode(signature.encode('ascii'))
