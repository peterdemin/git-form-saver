import os
from aiohttp import web
import aiohttp_debugtoolbar
import jinja2
import aiohttp_jinja2


HERE = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_PATH = os.path.join(HERE, 'templates')
app = web.Application()


async def save_form_to_git(request):
    form = await request.post()
    location = form.get('redirect') or request.headers.get('Referer')
    return web.HTTPFound(location)


@aiohttp_jinja2.template('test.html')
async def test_page(request):
    return {}


@aiohttp_jinja2.template('test.html')
async def test_done_page(request):
    return {}


def setup_app(app):
    aiohttp_debugtoolbar.setup(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES_PATH))
    app.router.add_post('/', save_form_to_git)
    app.router.add_routes([
        web.get('/test', test_page, name='test_page'),
        web.get('/tested', test_done_page, name='test_done_page'),
    ])



setup_app(app)
web.run_app(app)
