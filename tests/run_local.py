import logging

from aiohttp import web

from gitformsaver.http_server import setup_app

from .toy_service import ToyService


def setup_toy_app(app: web.Application) -> web.Application:
    setup_app(app)
    toy_service = ToyService()
    toy_service.setup(app)
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(setup_toy_app(web.Application()))


if __name__ == "__main__":
    main()
