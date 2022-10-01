import os
import pathlib
from unittest.mock import Mock

import pytest

from gitformsaver.git_task_handler import CloneTask, GitTaskHandler, WriteTask
from gitformsaver.lazy_git import LazyGit


def test_task_handler_clone_delegates_to_lazy_git(
    mock_lazy_git: LazyGit, git_task_handler: GitTaskHandler
) -> None:
    git_task_handler.handle_clone(CloneTask(url='url'))
    mock_lazy_git.clone.assert_called_once_with('url')


def test_task_handler_appends_text(
    mock_lazy_git: LazyGit,
    temp_repo_root: str,
    git_task_handler: GitTaskHandler,
) -> None:
    git_task_handler.handle_write(WriteTask(rel_path='rel-path', text='text'))
    mock_lazy_git.maybe_pull.assert_called_once_with()
    mock_lazy_git.maybe_push.assert_called_once()
    with open(os.path.join(temp_repo_root, 'rel-path'), encoding='ascii') as fobj:
        contents = fobj.read()
    assert contents == 'text'


@pytest.mark.parametrize('rel_path', ['/etc/hosts', '///////etc/hosts', 'inside-symlink'])
def test_task_handler_fixes_accidental_abs_path(
    mock_lazy_git: LazyGit,
    temp_repo_root: str,
    git_task_handler: GitTaskHandler,
    rel_path: str,
) -> None:
    git_task_handler.handle_write(WriteTask(rel_path=rel_path, text='text'))
    mock_lazy_git.maybe_pull.assert_called_once_with()
    mock_lazy_git.maybe_push.assert_called_once()
    with open(pathlib.Path(temp_repo_root) / 'etc' / 'hosts', encoding='ascii') as fobj:
        contents = fobj.read()
    assert contents == 'text'


@pytest.mark.parametrize(
    'rel_path',
    [
        '../out-of-repo',
        'in/and/../../../../../out',
        'outside-symlink',
    ],
)
def test_task_handler_detects_out_of_repo_path(
    mock_lazy_git: LazyGit,
    git_task_handler: GitTaskHandler,
    rel_path: str,
) -> None:
    git_task_handler.handle_write(WriteTask(rel_path=rel_path, text='text'))
    mock_lazy_git.maybe_pull.assert_called_once_with()
    mock_lazy_git.maybe_push.assert_not_called()


@pytest.fixture(name='temp_repo_root')
def _temp_repo_root(tmp_path: pathlib.Path) -> str:
    root = tmp_path / "root"
    root.mkdir()
    (root / 'outside-symlink').symlink_to('/etc/hosts')
    (root / 'inside-symlink').symlink_to(root / 'etc/hosts')
    (root / 'etc').mkdir()
    return str(root.absolute())


@pytest.fixture(name='mock_lazy_git')
def _mock_lazy_git(temp_repo_root: str) -> LazyGit:
    obj = Mock(spec_set=LazyGit)
    obj.root = temp_repo_root
    return obj


@pytest.fixture(name='git_task_handler')
def _git_task_handler(mock_lazy_git: LazyGit) -> GitTaskHandler:
    return GitTaskHandler(mock_lazy_git)
