import sys
from aiohttp import web

from .http_server import setup_app
from .authentication import Authentication


def generate_token() -> None:
    repo, path = sys.argv[1:3]
    print(Authentication().create_token(repo, path))


def run_http_server():
    app = web.Application()
    setup_app(app)
    web.run_app(app)
