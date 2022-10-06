import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from . import errors
from .authentication_interface import AuthenticationInterface
from .lazy_git import LazyGit

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class WriteTask:
    rel_path: str
    text: str
    secret: str = ''


@dataclass(frozen=True)
class CloneTask:
    url: str


@dataclass(frozen=True)
class GitTask:
    write_task: Optional[WriteTask] = None
    clone_task: Optional[CloneTask] = None


class GitTaskHandler:
    _COMMIT_MESSAGE = "Save form submission"

    def __init__(self, git: LazyGit, repo: str, authentication: AuthenticationInterface) -> None:
        self._git = git
        self._repo = repo
        self._authentication = authentication

    def handle_clone(self, clone_task: CloneTask) -> None:
        self._git.clone(clone_task.url)

    def handle_write(self, write_task: WriteTask) -> None:
        self._pull()
        is_ok, path = self._normalize_path(write_task.rel_path)
        if is_ok:
            token = self._read_token(path)
            self._validate_token(token, write_task.rel_path, secret=write_task.secret)
            self._write(path, write_task.text)
            self._push()

    def _normalize_path(self, path: str) -> Tuple[bool, str]:
        if os.path.isabs(path):
            path = os.path.relpath(path, '/')
        # Make sure the resulting path is inside the repo:
        abs_path = os.path.realpath(os.path.join(self._git.root, path))
        if not abs_path.startswith(self._git.root):
            LOG.warning("Haxor detected trying to write to abs path: %s as %s", abs_path, path)
            return False, ''
        return True, abs_path

    def _read_token(self, path: str) -> str:
        with open(path, mode="rt", encoding="utf-8") as fobj:
            token = self._authentication.extract_token(fobj.read(2048))
        if not token:
            raise errors.UserFacingError(
                "Couldn't find JWT token in the first 2048 bytes of the file"
            )
        LOG.debug("Found token: %s", token)
        return token

    def _validate_token(self, token: str, path: str, secret: str) -> None:
        if not self._authentication.is_valid_token(token, self._repo, path, secret):
            raise errors.UserFacingError("JWT token verification failed")

    def _write(self, path: str, text: str) -> None:
        with open(path, mode="a", encoding="utf-8") as fobj:
            fobj.write(text)

    def _pull(self) -> None:
        self._git.maybe_pull()

    def _push(self) -> None:
        self._git.maybe_push(self._COMMIT_MESSAGE)
