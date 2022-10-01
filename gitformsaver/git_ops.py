import os
import shutil
import logging

import git
from .git_client import Git

_HERE = os.path.dirname(__file__)
_SSH_EXECUTABLE = os.path.join(_HERE, 'ssh.sh')
LOG = logging.getLogger(__name__)


class GitOps:
    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path

    def clone(self, url: str, to_path: str) -> Git:
        git_env = {'GIT_SSH': _SSH_EXECUTABLE} if self._private_key_path else {}
        shutil.rmtree(to_path, ignore_errors=True)
        try:
            LOG.info("Cloning %s to %s", url, to_path)
            repo = git.Repo.clone_from(url=url, to_path=to_path, env=git_env)
        except git.GitCommandError as exc:
            raise git.GitError(exc.stderr.strip()) from exc
        return Git(repo)

    def existing(self, path: str) -> Git:
        LOG.info("Loading existing repo from %s", path)
        return Git(repo=git.Repo(path=path))
