from aiohttp import web

from .formatters_loader import load_formatters
from .git_ops import GitOps
from .git_thread_manager import GitThreadManager
from .authentication import Authentication
from .service import GitFormSaverService


def setup_app(app: web.Application) -> None:
    service = GitFormSaverService(
        git_thread_manager=GitThreadManager(
            git_ops=GitOps(private_key_path=""),
            authentication=Authentication(private_key_path=""),
        ),
        formatters=load_formatters(),
    )
    service.setup(app)
