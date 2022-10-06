from unittest import mock

import pytest

from gitformsaver.git_thread import GitThread
from gitformsaver.git_thread_manager import GitThreadManager
from gitformsaver.plain_text_formatter import PlainTextFormatter
from gitformsaver.formatters import Formatter
from gitformsaver.form_saver_service import GitFormSaverService

from .async_utils import run, FakeRequest


def test_minimal_valid_request(git_thread: GitThread, git_form_saver_service: GitFormSaverService):
    result = run(
        git_form_saver_service.handle(
            FakeRequest(
                {
                    'repo': 'git@github.com:user/repo.git',
                    'file': 'file',
                    'key': 'value',
                }
            )
        )
    )
    assert result.status == 302
    assert result.location == 'Referer'
    git_thread.push_soon.assert_called_once_with('file', 'key: value\n\n')


def test_full_request(git_thread: GitThread, git_form_saver_service: GitFormSaverService):
    result = run(
        git_form_saver_service.handle(
            FakeRequest(
                {
                    'repo': 'git@github.com:user/repo.git',
                    'file': 'file',
                    'redirect': 'http://example.com',
                    'formatter': 'JSON',
                    'key': 'value',
                }
            )
        )
    )
    assert result.status == 302
    assert result.location == 'http://example.com'
    git_thread.push_soon.assert_called_once_with('file', 'key: value\n\n')


def test_empty_request(git_form_saver_service: GitFormSaverService):
    result = run(git_form_saver_service.handle(FakeRequest({})))
    assert result.status == 400
    assert 'repo: Missing data for required field.' in result.text
    assert 'file: Missing data for required field.' in result.text


def test_bad_redirect_url(git_form_saver_service: GitFormSaverService):
    result = run(
        git_form_saver_service.handle(
            FakeRequest({'repo': 'repo', 'file': 'file', 'redirect': 'redirect'})
        )
    )
    assert result.status == 400
    assert result.text == 'redirect: Not a valid URL.'


@pytest.fixture(name='git_thread')
def _git_thread() -> GitThread:
    return mock.Mock(spec_set=GitThread)


@pytest.fixture(name='git_thread_manager')
def _git_thread_manager(git_thread: GitThread) -> GitThreadManager:
    obj = mock.Mock(spec_set=GitThreadManager)
    obj.return_value = git_thread
    return obj


@pytest.fixture(name='form_formatter')
def _form_formatter() -> PlainTextFormatter:
    return mock.Mock(wraps=PlainTextFormatter())


@pytest.fixture(name='git_form_saver_service')
def _git_form_saver_service(
    git_thread_manager: GitThreadManager, form_formatter: PlainTextFormatter
) -> GitFormSaverService:
    return GitFormSaverService(
        git_thread_manager=git_thread_manager,
        formatters={Formatter.PLAIN_TEXT: form_formatter, Formatter.JSON: form_formatter},
    )
