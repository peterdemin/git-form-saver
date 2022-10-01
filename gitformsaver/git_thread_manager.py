import os
import time
from dataclasses import dataclass
from typing import Dict

from .git_ops import GitOps
from .git_thread import GitThread
from .lazy_git import LazyGit
from .git_task_handler import GitTaskHandler
from .git_url_parse import parse_git_url


@dataclass(frozen=True)
class ThreadInfo:
    started_at: float
    git_thread: GitThread


class GitThreadManager:
    def __init__(self, git_ops: GitOps) -> None:
        self._threads: Dict[str, ThreadInfo] = {}
        self._git_ops = git_ops

    def __call__(self, repo: str) -> GitThread:
        if repo in self._threads and not self._threads[repo].git_thread.is_running:
            del self._threads[repo]
        if repo not in self._threads:
            git_thread = GitThread(
                GitTaskHandler(
                    LazyGit(self._make_repo_path(repo), self._git_ops)
                )
            )
            git_thread.clone_soon(repo)
            self._threads[repo] = ThreadInfo(started_at=time.time(), git_thread=git_thread)
        return self._threads[repo].git_thread

    def stop(self) -> None:
        for thread_info in self._threads.values():
            thread_info.git_thread.stop(block=False)
        for thread_info in self._threads.values():
            thread_info.git_thread.stop(block=True)

    def _make_repo_path(self, repo: str) -> str:
        # pylint: disable=consider-using-f-string
        parts = parse_git_url(repo)
        if not parts.resource:
            # No host
            return ''
        if set(parts.protocols) - {'ssh', 'git'}:
            # Unsupported URL schema
            return ''
        path = '{}/{}'.format(parts.resource, parts.pathname.lstrip('/'))
        canonical_path = os.path.relpath(f'/{path}', '/')
        prefix = os.path.commonprefix((path, canonical_path))
        if prefix == path:
            return path
        return ''
