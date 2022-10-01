# pylint: disable=redefined-outer-name
from unittest import mock

import pytest

from gitformsaver.git_client import Git
from gitformsaver.git_ops import GitOps
from gitformsaver.git_thread_manager import GitThreadManager


@pytest.mark.parametrize(
    'url, path',
    [
        (
            'git@github.com:peterdemin/git-form-saver-demo.git',
            'github.com/peterdemin/git-form-saver-demo.git',
        ),
        (
            'ssh://git@github.com:peterdemin/git-form-saver-demo.git',
            'github.com/peterdemin/git-form-saver-demo.git',
        ),
        (
            'ssh://user:password@host:dir',
            'host/dir',
        ),
        (
            'ssh://user:password@host:/etc/hosts',
            'host/etc/hosts',
        ),
        ('https://github.com/coala/git-url-parse.git', ''),
        ('ssh://user:password@host:../../../../etc/hosts', ''),
        ('file:///etc/hosts', ''),
    ],
)
def test_thread_manager_creates_git_thread(
    mock_git_ops: GitOps, git_thread_manager: GitThreadManager, url: str, path: str
) -> None:
    git_thread_manager(url)
    git_thread_manager.stop()
    mock_git_ops.clone.assert_called_once_with(url=url, to_path=path)


@pytest.fixture(name='mock_git_ops')
def _mock_git_ops() -> GitOps:
    obj = mock.Mock(spec_set=GitOps)
    obj.clone.return_value = mock.Mock(spec_set=Git)
    obj.existing.return_value = mock.Mock(spec_set=Git)
    return obj


@pytest.fixture(name='git_thread_manager')
def _git_thread_manager(mock_git_ops: GitOps) -> GitThreadManager:
    return GitThreadManager(git_ops=mock_git_ops)
