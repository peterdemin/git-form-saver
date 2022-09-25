import queue
import threading
from typing import Iterable

from .git_client import Git


class GitThread:
    _POLL_TIMEOUT = 1
    _SHUTDOWN_TIMEOUT = 5
    _COMMIT_MESSAGE = "Save form submission"
    _DELIMITER = "\n\n"

    def __init__(self, git: Git, file_path: str) -> None:
        self._git = git
        self._file_path = file_path
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_thread)
        self._running = True
        self._thread.start()

    def push_soon(self, text: str) -> None:
        self._queue.put(text)

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
            self._pull()
            self._write(
                "".join(text + self._DELIMITER
                        for text in self._pull_pending_texts())
            )
            self._push()

    def _pull_pending_texts(self) -> Iterable[str]:
        while not self._queue.empty():
            item = self._queue.get()
            self._queue.task_done()
            yield item

    def _write(self, text: str) -> None:
        with open(self._file_path, mode="a", encoding="utf-8") as fobj:
            fobj.write(text)

    def _pull(self) -> None:
        self._git.maybe_pull()

    def _push(self) -> None:
        self._git.maybe_push(self._COMMIT_MESSAGE)
