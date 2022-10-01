from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import aiohttp
import marshmallow
from aiohttp import web
from multidict import MultiDictProxy

from .git_ops import GitOps
from .git_thread_manager import GitThreadManager
from .formatters_loader import load_formatters
from .formatters import Formatter

FORMS_REPO_PATH = "forms"
FORM_FILE_PATH = "README.md"


@dataclass(frozen=True)
class Control:
    repo: str
    file: str
    formatter: Formatter = Formatter.PLAIN_TEXT
    redirect: str = ''


class ControlSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE

    repo = marshmallow.fields.String(required=True)
    file = marshmallow.fields.String(required=True)
    formatter = marshmallow.fields.Enum(Formatter, load_default=Formatter.PLAIN_TEXT)
    redirect = marshmallow.fields.URL()

    @marshmallow.post_load
    def make_control(self, data, **kwargs):
        del kwargs
        return Control(**data)


class GitFormSaverService:
    def __init__(
        self,
        git_thread_manager: GitThreadManager,
        formatters: Dict[Formatter, Callable[[List[Tuple[str, str]]], str]],
    ) -> None:
        self._git_thread_manager = git_thread_manager
        self._control_schema = ControlSchema()
        self._formatters = formatters

    async def handle(self, request: aiohttp.web.Request) -> web.HTTPFound:
        form_data = await request.post()
        control, pairs, error = self._parse_data(form_data)
        if not error:
            text = self._formatters[control.formatter](pairs)
            if text:
                self._git_thread_manager(control.repo).push_soon(
                    control.file, text
                )
            return web.HTTPFound(control.redirect or request.headers.get("Referer"))
        return web.HTTPBadRequest(text=error)

    def _parse_data(
        self, form_data: MultiDictProxy
    ) -> Tuple[ControlSchema, List[Tuple[str, str]], marshmallow.ValidationError]:
        try:
            return (*self._unsafe_parse_data(form_data), None)
        except marshmallow.ValidationError as exc:
            return (None, None, self._format_validation_error(exc))

    def _unsafe_parse_data(
        self, form_data: MultiDictProxy
    ) -> Tuple[ControlSchema, List[Tuple[str, str]]]:
        control = self._control_schema.load(form_data)
        pairs: List[Tuple[str, str]] = []
        for key in form_data:
            if key not in self._control_schema.declared_fields:
                pairs.extend((key, value) for value in form_data.getall(key))
        return control, pairs

    def _format_validation_error(self, exc: marshmallow.ValidationError) -> str:
        return '\n'.join(
            f'{key}: {" ".join(values)}'
            for key, values in exc.messages.items()
        )

    def setup(self, app: web.Application) -> None:
        app.router.add_post("/", self.handle)
        app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, app: web.Application) -> None:
        del app
        self._git_thread_manager.stop()


def setup_app(app: web.Application) -> None:
    service = GitFormSaverService(
        git_thread_manager=GitThreadManager(
            git_ops=GitOps(private_key_path=""),
        ),
        formatters=load_formatters(),
    )
    service.setup(app)


def main():
    app = web.Application()
    setup_app(app)
    web.run_app(app)


if __name__ == "__main__":
    main()
