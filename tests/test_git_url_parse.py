import pytest
from gitformsaver.git_url_parse import parse_git_url


@pytest.mark.parametrize(
    'url',
    [
        'git@github.com:owner/repo',
        'git@github.com:peterdemin/peterdemin.github.io',
    ]
)
def test_valid_url_parsed(url):
    parse_git_url(url)
