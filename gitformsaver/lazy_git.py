import os

from .git_client import GitInterface, Git
from .git_ops import GitOps


class LazyGit(GitInterface):
    def __init__(self, path: str, git_ops: GitOps) -> None:
        # pylint: disable=super-init-not-called
        self._path = path
        self._git_ops = git_ops
        self._actual_git: Git = None

    def clone(self, url: str) -> None:
        self._actual_git = self._git_ops.clone(url=url, to_path=self._path)

    def push(self) -> None:
        self._git.push()

    def maybe_pull(self) -> None:
        """Download remote changes if copy is clean."""
        self._git.maybe_pull()

    def maybe_push(self, commit_message: str) -> None:
        """Add-commit-push changes."""
        self._git.maybe_push(commit_message)

    @property
    def root(self) -> str:
        return os.path.abspath(self._path)

    @property
    def _git(self) -> Git:
        if self._actual_git is None:
            self._actual_git = self._git_ops.existing(self._path)
        return self._actual_git
