import queue
import threading
from dataclasses import dataclass
from typing import Iterable

from .lazy_git import LazyGit


@dataclass(frozen=True)
class WriteTask:
    path: str
    text: str


@dataclass(frozen=True)
class CloneTask:
    url: str


@dataclass(frozen=True)
class GitTask:
    write_task: WriteTask = None
    clone_task: CloneTask = None


class GitThread:
    _POLL_TIMEOUT = 1
    _SHUTDOWN_TIMEOUT = 5
    _COMMIT_MESSAGE = "Save form submission"
    _DELIMITER = "\n\n"

    def __init__(self, git: LazyGit) -> None:
        self._git = git
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_thread)
        self._running = True
        self._thread.start()

    def push_soon(self, path: str, text: str) -> None:
        self._queue.put(GitTask(write_task=WriteTask(path=path, text=text)))

    def clone_soon(self, url: str) -> None:
        self._queue.put(GitTask(clone_task=CloneTask(url=url)))

    def stop(self, block: bool = True) -> None:
        self._running = False
        if block:
            self._queue.join()
            self._thread.join(timeout=self._SHUTDOWN_TIMEOUT)

    def _run_thread(self) -> None:
        while self._running:
            try:
                with self._queue.not_empty:
                    self._queue.not_empty.wait(timeout=self._POLL_TIMEOUT)
            except queue.Empty:
                continue
            for task in self._batch(self._flush()):
                self._write(task.path, task.text)
            self._push()

    def _batch(self, tasks: Iterable[WriteTask]) -> Iterable[WriteTask]:
        path, parts = '', []
        for task in tasks:
            if task.path == path:
                parts.append(task.text)
            else:
                if path and parts:
                    yield WriteTask(path, "".join(part + self._DELIMITER for part in parts))
                path, parts = task.path, [task.text]
        if path and parts:
            yield WriteTask(path, "".join(part + self._DELIMITER for part in parts))

    def _flush(self) -> Iterable[WriteTask]:
        while not self._queue.empty():
            task = self._queue.get()
            self._queue.task_done()
            if task.clone_task:
                self._git.clone(task.clone_task.url)
            if task.write_task:
                self._pull()
                yield task.write_task

    def _write(self, path: str, text: str) -> None:
        with open(path, mode="a", encoding="utf-8") as fobj:
            fobj.write(text)

    def _pull(self) -> None:
        self._git.maybe_pull()

    def _push(self) -> None:
        self._git.maybe_push(self._COMMIT_MESSAGE)
