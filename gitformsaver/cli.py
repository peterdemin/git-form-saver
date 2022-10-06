import sys
import logging
from aiohttp import web

from .http_server import setup_app
from .authentication import Authentication


def generate_token() -> None:
    logging.basicConfig(level=logging.DEBUG)
    repo, path = sys.argv[1:3]
    print(Authentication().create_token(repo, path))


def run_http_server():
    logging.basicConfig(level=logging.INFO)
    web.run_app(setup_app(web.Application()))
