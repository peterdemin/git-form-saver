import os
import shutil

import git
from .git_client import Git

_HERE = os.path.dirname(__file__)
_SSH_EXECUTABLE = os.path.join(_HERE, 'ssh.sh')


class GitOps:
    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path

    def clone(self, url: str, to_path: str) -> Git:
        git_env = {'GIT_SSH': _SSH_EXECUTABLE} if self._private_key_path else {}
        shutil.rmtree(to_path, ignore_errors=True)
        try:
            repo = git.Repo.clone_from(url=url, to_path=to_path, env=git_env)
        except git.GitCommandError as exc:
            raise git.GitError(exc.stderr.strip()) from exc
        return Git(repo)

    def existing(self, path: str) -> Git:
        return Git(repo=git.Repo(path=path))
