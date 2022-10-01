from aiohttp import web

from gitformsaver.form_formatter import FormFormatter
from gitformsaver.formatters import Formatter
from gitformsaver.git_ops import GitOps
from gitformsaver.git_thread_manager import GitThreadManager
from gitformsaver.http_server import GitFormSaverService

from .toy_service import ToyService

_app = web.Application()


def setup_app(app: web.Application) -> None:
    service = GitFormSaverService(
        git_thread_manager=GitThreadManager(
            git_ops=GitOps(private_key_path=""),
        ),
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
