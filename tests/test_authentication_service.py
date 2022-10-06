from unittest import mock

import pytest

from gitformsaver.authentication_interface import AuthenticationInterface
from gitformsaver.authentication_service import AuthenticationService

from .async_utils import FakeRequest, run


@pytest.mark.parametrize('secret', ['', 'secret'])
def test_valid_request(
    authentication_service: AuthenticationService,
    mock_authentication: AuthenticationInterface,
    secret: str,
) -> None:
    payload = {'repo': 'git@github.com:user/repo.git', 'file': 'file', 'secret': secret}
    result = run(authentication_service.handle(FakeRequest(payload)))
    assert result.status == 200
    assert result.text == 'token'
    mock_authentication.create_token.assert_called_once_with(
        repo='git@github.com:user/repo.git', path='file', secret=secret
    )


def test_incomplete_request_rejected(
    authentication_service: AuthenticationService, mock_authentication: AuthenticationInterface
) -> None:
    payload = {'repo': 'git@github.com:user/repo.git'}
    result = run(authentication_service.handle(FakeRequest(payload)))
    assert result.status == 400
    assert result.text == 'file: Missing data for required field.'
    mock_authentication.create_token.assert_not_called()


@pytest.fixture(name='mock_authentication')
def _mock_authentication() -> AuthenticationInterface:
    obj = mock.Mock(spec_set=AuthenticationInterface)
    obj.create_token.return_value = 'token'
    return obj


@pytest.fixture(name='authentication_service')
def _authentication_service(mock_authentication: AuthenticationInterface) -> AuthenticationService:
    return AuthenticationService(authentication=mock_authentication)
