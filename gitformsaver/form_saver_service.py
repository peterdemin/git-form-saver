from dataclasses import dataclass
from typing import List, Mapping, Optional, Tuple, Union

import aiohttp
import marshmallow
from aiohttp import web
from multidict import MultiDictProxy

from .formatters import Formatter, FormatterInterface
from .git_thread_manager import GitThreadManager

FORMS_REPO_PATH = "forms"
FORM_FILE_PATH = "README.md"
Pairs = List[Tuple[str, str]]


@dataclass(frozen=True)
class Control:
    repo: str
    file: str
    formatter: Formatter = Formatter.PLAIN_TEXT
    redirect: str = ''


@dataclass(frozen=True)
class Payload:
    control: Optional[Control]
    pairs: Pairs
    error: str


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
    _control_schema = ControlSchema()

    def __init__(
        self,
        git_thread_manager: GitThreadManager,
        formatters: Mapping[Formatter, FormatterInterface],
    ) -> None:
        self._git_thread_manager = git_thread_manager
        self._formatters = formatters

    async def handle(
        self, request: aiohttp.web.Request
    ) -> Union[web.HTTPFound, web.HTTPBadRequest]:
        form_data = await request.post()
        payload = self._parse_data(form_data)
        if payload.error or not payload.control or not payload.pairs:
            return web.HTTPBadRequest(text=payload.error)
        text = self._formatters[payload.control.formatter](payload.pairs)
        if text:
            self._git_thread_manager(payload.control.repo).push_soon(payload.control.file, text)
        return web.HTTPFound(
            payload.control.redirect or request.headers["Referer"]
        )

    def _parse_data(self, form_data: MultiDictProxy) -> Payload:
        try:
            control, pairs = self._unsafe_parse_data(form_data)
            return Payload(control=control, pairs=pairs, error='')
        except marshmallow.ValidationError as exc:
            return Payload(control=None, pairs=[], error=self._format_validation_error(exc))

    def _unsafe_parse_data(
        self, form_data: MultiDictProxy
    ) -> Tuple[Control, List[Tuple[str, str]]]:
        control = self._control_schema.load(form_data)
        pairs: List[Tuple[str, str]] = []
        for key in form_data:
            if key not in self._control_schema.declared_fields:
                pairs.extend((key, value) for value in form_data.getall(key))
        return control, pairs

    def _format_validation_error(self, exc: marshmallow.ValidationError) -> str:
        return '\n'.join(f'{key}: {" ".join(values)}' for key, values in exc.messages_dict.items())

    def setup(self, app: web.Application) -> None:
        app.router.add_post("/", self.handle)
        app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, app: web.Application) -> None:
        del app
        self._git_thread_manager.stop()
