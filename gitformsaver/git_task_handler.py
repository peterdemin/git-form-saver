import logging
import os
from dataclasses import dataclass
from typing import Tuple

from .lazy_git import LazyGit

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class WriteTask:
    rel_path: str
    text: str


@dataclass(frozen=True)
class CloneTask:
    url: str


@dataclass(frozen=True)
class GitTask:
    write_task: WriteTask = None
    clone_task: CloneTask = None


class GitTaskHandler:
    _COMMIT_MESSAGE = "Save form submission"

    def __init__(self, git: LazyGit) -> None:
        self._git = git

    def handle_clone(self, clone_task: CloneTask) -> None:
        self._git.clone(clone_task.url)

    def handle_write(self, write_task: WriteTask) -> None:
        self._pull()
        is_ok, path = self._normalize_path(write_task.rel_path)
        if is_ok:
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

    def _write(self, path: str, text: str) -> None:
        with open(path, mode="a", encoding="utf-8") as fobj:
            fobj.write(text)

    def _pull(self) -> None:
        self._git.maybe_pull()

    def _push(self) -> None:
        self._git.maybe_push(self._COMMIT_MESSAGE)
