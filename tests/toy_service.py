import os

from aiohttp import web

try:
    import aiohttp_debugtoolbar
    import aiohttp_jinja2
    import jinja2

    _DEBUG_ENABLED = True
except ImportError:
    _DEBUG_ENABLED = False


HERE = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_PATH = os.path.join(HERE, "templates")


class ToyService:
    def setup(self, app) -> None:
        if not _DEBUG_ENABLED:
            return
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES_PATH))
        aiohttp_debugtoolbar.setup(app)
        app.router.add_routes(
            [
                web.get("/test", self.test_page, name="test_page"),
                web.get("/tested", self.test_done_page, name="test_done_page"),
            ]
        )

    @aiohttp_jinja2.template("test.html")
    async def test_page(self, request):
        return {'base_url': f'{request.scheme}://{request.host}'}

    @aiohttp_jinja2.template("test.html")
    async def test_done_page(self, request):
        return {'base_url': f'{request.scheme}://{request.host}'}
