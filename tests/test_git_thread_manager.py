# pylint: disable=redefined-outer-name
from unittest import mock

import pytest

from gitformsaver.git_client import Git
from gitformsaver.git_ops import GitOps
from gitformsaver.git_thread_manager import GitThreadManager


def test_thread_manager_creates_git_thread(
    mock_git_ops: GitOps, git_thread_manager: GitThreadManager
) -> None:
    git_thread_manager('repo-url')
    git_thread_manager.stop()
    mock_git_ops.clone.assert_called_once_with(url='repo-url', to_path='/repo-url')


@pytest.fixture(name='mock_git_ops')
def _mock_git_ops() -> GitOps:
    obj = mock.Mock(spec_set=GitOps)
    obj.clone.return_value = mock.Mock(spec_set=Git)
    obj.existing.return_value = mock.Mock(spec_set=Git)
    return obj


@pytest.fixture(name='git_thread_manager')
def _git_thread_manager(mock_git_ops: GitOps) -> GitThreadManager:
    return GitThreadManager(git_ops=mock_git_ops)
