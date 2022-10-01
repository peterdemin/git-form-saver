import os

from aiohttp import web
import git

from gitformsaver.http_server import GitFormSaverService
from gitformsaver.git_thread import GitThread
from gitformsaver.git_client import Git
from gitformsaver.form_formatter import FormFormatter
from gitformsaver.formatters import Formatter
from .toy_service import ToyService

_app = web.Application()


def setup_app(app: web.Application) -> None:
    git_thread = GitThread(
        git=Git(
            repo=git.Repo('forms'),
            private_key_path="",
        ),
        file_path=os.path.join('forms', 'README.md'),
    )
    service = GitFormSaverService(
        git_thread=git_thread,
        formatters={Formatter.PLAIN_TEXT: FormFormatter()},
    )
    service.setup(app)
    toy_service = ToyService()
    toy_service.setup(app)


def main():
    setup_app(_app)
    web.run_app(_app)


if __name__ == "__main__":
    main()
