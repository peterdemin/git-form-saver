from unittest.mock import call

_REPO = 'git@github.com:user/repo.git'
_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'text/plain; charset=utf-8',
}


TEST_CASES = [
    dict(
        name='success_with_secret',
        parameters={'repo': _REPO, 'file': 'file', 'secret': 'secret'},
        expected=dict(
            status=200,
            text='token',
            headers=_HEADERS,
            create_token=[call(repo=_REPO, path='file', secret='secret')],
        ),
    ),
    dict(
        name='success_with_empty_secret',
        parameters={'repo': _REPO, 'file': 'file', 'secret': ''},
        expected=dict(
            status=200,
            text='token',
            headers=_HEADERS,
            create_token=[call(repo=_REPO, path='file', secret='')],
        ),
    ),
    dict(
        name='success_without_secret',
        parameters={'repo': _REPO, 'file': 'file'},
        expected={
            'status': 200,
            'text': 'token',
            'headers': _HEADERS,
            'create_token': [call(repo=_REPO, path='file', secret='')],
        },
    ),
    dict(
        name='missing_file_failure',
        parameters={'repo': _REPO},
        expected=dict(
            status=400,
            text='file: Missing data for required field.',
            headers=_HEADERS,
            create_token=[],
        ),
    ),
]
