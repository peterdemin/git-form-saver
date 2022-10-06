import hmac
import logging
import os
import re
from functools import cached_property
from typing import Dict, cast

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.ssh import load_ssh_private_key

from .authentication_interface import AuthenticationInterface

LOG = logging.getLogger(__name__)


class Authentication(AuthenticationInterface):
    _ALGORITHM = "RS256"
    _HASH_ALGORITHM = "SHA256"
    _TEMPLATE = 'GFS-JWT:{}'
    _RE_JWT_TOKEN = re.compile('GFS-JWT:([a-zA-Z0-9._-]{32,1000})')

    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path or os.path.expanduser("~/.ssh/id_rsa")

    def create_token(self, repo: str, path: str, secret: str = '') -> str:
        return self._TEMPLATE.format(self._encode(self._format_payload(repo, path, secret)))

    def extract_token(self, text: str) -> str:
        matchobj = self._RE_JWT_TOKEN.search(text)
        if matchobj:
            return matchobj.group(1)
        return ''

    def is_valid_token(self, token: str, repo: str, path: str, secret: str = '') -> bool:
        try:
            decoded = self._decode(token)
            expected = self._format_payload(repo, path, secret)
            if decoded == expected:
                return True
            LOG.debug("Expected token: %s", expected)
            LOG.debug("Decoded token:  %s", decoded)
        except jwt.exceptions.InvalidSignatureError:
            LOG.exception("Invalid signature")
        return False

    def _format_payload(self, repo: str, path: str, secret: str) -> Dict[str, str]:
        key = (secret or 'secret').encode('utf-8')
        msg = f'{repo} {path}'.encode('utf-8')
        LOG.debug("Generating payload: key: %s, msg: %s", key, msg)
        result = {
            self._HASH_ALGORITHM: hmac.new(
                key=key, msg=msg, digestmod=self._HASH_ALGORITHM.lower()
            ).hexdigest()
        }
        LOG.debug("Payload: %s", result)
        return result

    def _encode(self, payload: Dict[str, str]) -> str:
        return jwt.encode(
            payload=payload, key=cast(str, self._private_key), algorithm=self._ALGORITHM
        )

    def _decode(self, token: str) -> Dict[str, str]:
        return jwt.decode(jwt=token, key=cast(str, self._public_key), algorithms=[self._ALGORITHM])

    @cached_property
    def _private_key(self) -> rsa.RSAPrivateKey:
        with open(self._private_key_path, "rb") as fobj:
            # Only RSA supports signing
            return cast(rsa.RSAPrivateKey, load_ssh_private_key(fobj.read(), password=None))

    @cached_property
    def _public_key(self) -> rsa.RSAPublicKey:
        return self._private_key.public_key()
