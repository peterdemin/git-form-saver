from aiohttp import web

from .formatters_loader import load_formatters
from .git_ops import GitOps
from .git_thread_manager import GitThreadManager
from .authentication import Authentication
from .form_saver_service import GitFormSaverService
from .authentication_service import AuthenticationService


def setup_app(app: web.Application) -> web.Application:
    private_key_path = ""
    authentication = Authentication(private_key_path=private_key_path)
    form_saver_service = GitFormSaverService(
        git_thread_manager=GitThreadManager(
            git_ops=GitOps(private_key_path=private_key_path),
            authentication=authentication,
        ),
        formatters=load_formatters(),
    )
    authentication_service = AuthenticationService(authentication=authentication)
    form_saver_service.setup(app)
    authentication_service.setup(app)
    return app
