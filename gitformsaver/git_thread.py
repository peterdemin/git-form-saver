import queue
import threading
from typing import Iterable

from .git_task_handler import GitTask, WriteTask, CloneTask, GitTaskHandler


class GitThread:
    _POLL_TIMEOUT = 1
    _SHUTDOWN_TIMEOUT = 5

    def __init__(self, git_task_handler: GitTaskHandler) -> None:
        self._handler = git_task_handler
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_thread)
        self._running = True
        self._thread.start()

    def push_soon(self, rel_path: str, text: str) -> None:
        # TODO: Add check that thread is running
        self._queue.put(GitTask(write_task=WriteTask(rel_path=rel_path, text=text)))

    def clone_soon(self, url: str) -> None:
        self._queue.put(GitTask(clone_task=CloneTask(url=url)))

    def stop(self, block: bool = True) -> None:
        self._running = False
        if not self._thread.is_alive():
            return
        if block:
            self._queue.join()
            self._thread.join(timeout=self._SHUTDOWN_TIMEOUT)

    @property
    def is_running(self) -> bool:
        return self._running and self._thread.is_alive()

    def _run_thread(self) -> None:
        while self._running:
            try:
                with self._queue.not_empty:
                    self._queue.not_empty.wait(timeout=self._POLL_TIMEOUT)
            except queue.Empty:
                continue
            # TODO: Stop _running on error
            for task in self._batch(self._flush()):
                self._handler.handle_write(task)

    def _batch(self, tasks: Iterable[WriteTask]) -> Iterable[WriteTask]:
        rel_path, parts = '', []
        for task in tasks:
            if task.rel_path == rel_path:
                parts.append(task.text)
            else:
                if rel_path and parts:
                    yield WriteTask(rel_path, "".join(parts))
                rel_path, parts = task.rel_path, [task.text]
        if rel_path and parts:
            yield WriteTask(rel_path, "".join(parts))

    def _flush(self) -> Iterable[WriteTask]:
        while not self._queue.empty():
            task = self._queue.get()
            self._queue.task_done()
            if task.clone_task:
                self._handler.handle_clone(task.clone_task)
            if task.write_task:
                yield task.write_task
