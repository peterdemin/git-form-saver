from dataclasses import dataclass
from typing import Union

import aiohttp
import marshmallow
from aiohttp import web

from .authentication_interface import AuthenticationInterface


@dataclass(frozen=True)
class Control:
    repo: str
    file: str
    secret: str


class ControlSchema(marshmallow.Schema):
    repo = marshmallow.fields.String(required=True)
    file = marshmallow.fields.String(required=True)
    secret = marshmallow.fields.String(required=False)

    @marshmallow.post_load
    def make_control(self, data, **kwargs):
        del kwargs
        return Control(**data)


class AuthenticationService:
    _control_schema = ControlSchema()

    def __init__(self, authentication: AuthenticationInterface) -> None:
        self._authentication = authentication

    async def handle(
        self, request: aiohttp.web.Request
    ) -> Union[web.HTTPOk, web.HTTPBadRequest]:
        try:
            control = self._control_schema.load(await request.post())
        except marshmallow.ValidationError as exc:
            return web.HTTPBadRequest(text=self._format_validation_error(exc))
        return web.HTTPOk(
            text=self._authentication.create_token(
                repo=control.repo,
                path=control.file,
                secret=control.secret,
            )
        )

    def _format_validation_error(self, exc: marshmallow.ValidationError) -> str:
        return '\n'.join(f'{key}: {" ".join(values)}' for key, values in exc.messages_dict.items())

    def setup(self, app: web.Application) -> None:
        app.router.add_post("/token", self.handle)
