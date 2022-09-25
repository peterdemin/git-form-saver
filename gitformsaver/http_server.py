import os
from typing import Callable, List, Tuple

import aiohttp
import git
from aiohttp import web
from multidict import MultiDictProxy

from .async_git_client import GitThread
from .git_client import Git
from .form_formatter import FormFormatter

FORMS_REPO_PATH = "forms"
FORM_FILE_PATH = "README.md"


class GitFormSaverService:
    def __init__(
        self,
        git_thread: GitThread,
        form_formatter: Callable[[List[Tuple[str, str]]], str],
    ) -> None:
        self._git_thread = git_thread
        self._form_formatter = form_formatter

    async def handle(self, request: aiohttp.web.Request) -> web.HTTPFound:
        location = request.headers.get("Referer")
        form: MultiDictProxy = await request.post()
        pairs: List[Tuple[str, str]] = []
        for key in form:
            if key == "redirect":
                location = form.getone(key)
            else:
                pairs.extend(
                    (key, value)
                    for value in form.getall(key)
                )
        text = self._form_formatter(pairs)
        if text:
            self._git_thread.push_soon(text)
        return web.HTTPFound(location)

    def setup(self, app: web.Application) -> None:
        app.router.add_post("/", self.handle)
        app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, app: web.Application) -> None:
        del app
        self._git_thread.stop()


def setup_app(app: web.Application) -> None:
    git_thread = GitThread(
        git=Git(
            repo=git.Repo(FORMS_REPO_PATH),
            private_key_path="",
        ),
        file_path=os.path.join(FORMS_REPO_PATH, FORM_FILE_PATH),
    )
    service = GitFormSaverService(
        git_thread=git_thread,
        form_formatter=FormFormatter(),
    )
    service.setup(app)


def main():
    app = web.Application()
    setup_app(app)
    web.run_app(app)


if __name__ == "__main__":
    main()
