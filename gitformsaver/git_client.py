import git


class GitInterface:
    def push(self):
        raise NotImplementedError()

    def maybe_pull(self) -> None:
        raise NotImplementedError()

    def maybe_push(self, commit_message: str) -> None:
        raise NotImplementedError()


class Git(GitInterface):
    def __init__(self, repo: git.Repo) -> None:
        self._repo = repo

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
