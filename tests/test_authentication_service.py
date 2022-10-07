from typing import Dict
from unittest import mock

import pytest

from gitformsaver.authentication_interface import AuthenticationInterface
from gitformsaver.authentication_service import AuthenticationService

from .async_utils import FakeRequest, run
from .golden_utils import assert_golden, load_test_cases
from .testdata.authentication_service_test_cases import TEST_CASES


@load_test_cases(TEST_CASES)
def test_authentication_service_test_cases(
    authentication_service: AuthenticationService,
    mock_authentication: AuthenticationInterface,
    name: str,
    parameters: Dict[str, str],
    expected: dict,
) -> dict:
    response = run(authentication_service.handle(FakeRequest(parameters)))
    assert_golden(
        name,
        expected,
        {
            'status': response.status,
            'text': response.text,
            'headers': dict(response.headers),
            'create_token': mock_authentication.create_token.call_args_list,
        },
    )


@pytest.fixture(name='mock_authentication')
def _mock_authentication() -> AuthenticationInterface:
    obj = mock.Mock(spec_set=AuthenticationInterface)
    obj.create_token.return_value = 'token'
    return obj


@pytest.fixture(name='authentication_service')
def _authentication_service(mock_authentication: AuthenticationInterface) -> AuthenticationService:
    return AuthenticationService(authentication=mock_authentication)
