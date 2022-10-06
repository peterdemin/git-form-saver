from aiohttp import web
from gitformsaver.http_server import setup_app


def test_can_setup_app() -> None:
    setup_app(web.Application())
