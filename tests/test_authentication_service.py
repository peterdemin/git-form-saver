from unittest import mock, TestCase

from gitformsaver.authentication_interface import AuthenticationInterface
from gitformsaver.authentication_service import AuthenticationService

from .async_utils import FakeRequest, run
from .golden_utils import golden_test
from .testdata.authentication_service_test_cases import TEST_CASES


@golden_test(TEST_CASES)
class AuthenticationServiceTestCase(TestCase):
    def setUp(self) -> None:
        self._mock_authentication = mock.Mock(spec_set=AuthenticationInterface)
        self._mock_authentication.create_token.return_value = 'token'
        self._authentication_service = AuthenticationService(
            authentication=self._mock_authentication
        )

    def produce(self, parameters: dict) -> dict:
        response = run(self._authentication_service.handle(FakeRequest(parameters)))
        return {
            'status': response.status,
            'text': response.text,
            'headers': dict(response.headers),
            'create_token': self._mock_authentication.create_token.call_args_list,
        }
