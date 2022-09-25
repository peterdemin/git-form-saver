import os

import aiohttp_jinja2
import jinja2
from aiohttp import web
import git

from .async_git_client import GitThread
from .git_client import Git

try:
    import aiohttp_debugtoolbar

    _DEBUG_ENABLED = True
except ImportError:
    _DEBUG_ENABLED = False


HERE = os.path.abspath(os.path.dirname(__file__))
FORMS_REPO_PATH = 'forms'
FORM_FILE_PATH = 'README.md'
TEMPLATES_PATH = os.path.join(HERE, "templates")
app = web.Application()


class GitFormSaverService:
    def __init__(self, git_thread: GitThread) -> None:
        self._git_thread = git_thread

    async def __call__(self, request: web.Request) -> web.HTTPFound:
        form = await request.post()
        location = form.get("redirect") or request.headers.get("Referer")
        return web.HTTPFound(location)

    def setup(self, app: web.Application) -> None:
        app.router.add_post("/", self)


class TestService:
    def setup(self, app) -> None:
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
        del request
        return {}


    @aiohttp_jinja2.template("test.html")
    async def test_done_page(self, request):
        del request
        return {}


def setup_app(app: web.Application) -> None:
    service = GitFormSaverService(
        GitThread(
            git=Git(
                repo=git.Repo(FORMS_REPO_PATH),
                private_key_path='',
            ),
            file_path=os.path.join(FORMS_REPO_PATH, FORM_FILE_PATH),
        )
    )
    service.setup(app)
    if _DEBUG_ENABLED:
        TestService().setup(app)


def main():
    setup_app(app)
    web.run_app(app)


if __name__ == "__main__":
    main()
