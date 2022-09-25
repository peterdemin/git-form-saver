import os

import git


_HERE = os.path.dirname(__file__)
_SSH_EXECUTABLE = os.path.join(_HERE, 'ssh.sh')


class GitOps:
    def __init__(self, private_key_path: str = '') -> None:
        self._private_key_path = private_key_path

    def clone(self, url: str, to_path: str) -> 'Git':
        git_env = (
            {'GIT_SSH': _SSH_EXECUTABLE}
            if self._private_key_path
            else {}
        )
        try:
            repo = git.Repo.clone_from(url=url, to_path=to_path, env=git_env)
        except git.GitCommandError as exc:
            raise GitError(exc.stderr.strip()) from exc
        return Git(repo, private_key_path=self._private_key_path)


class Git:
    def __init__(self, repo: git.Repo, private_key_path: str) -> None:
        self._repo = repo
        if private_key_path:
            self._repo.git.update_environment(GIT_SSH=_SSH_EXECUTABLE)

    def push(self):
        try:
            self._repo.remotes[0].push()
        except git.GitCommandError as exc:
            raise GitError(exc.stderr.strip()) from exc

    def maybe_pull(self) -> None:
        """Download remote changes if copy is clean."""
        if self._is_clean():
            self._repo.remotes[0].pull()

    def maybe_push(self, commit_message: str) -> None:
        """Add-commit-push changes."""
        self._repo.git.add(A=True)
        if not self._is_clean():
            self._repo.index.commit(commit_message)
            self.push()

    def _is_clean(self) -> bool:
        return not self._repo.is_dirty()


class GitError(RuntimeError):
    def __init__(self, stderr: str) -> None:
        self.stderr = stderr
        super().__init__(stderr)
