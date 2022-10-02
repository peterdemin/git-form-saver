# Adapted from git-url-parse package:

# Copyright (c) 2017 John Dewey
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

from typing import Optional, List
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Parsed:  # pylint: disable=too-many-instance-attributes
    pathname: Optional[str]
    protocols: List[str]
    protocol: str
    href: str
    resource: Optional[str]
    user: Optional[str]
    port: Optional[str]


def parse_git_url(url):
    return _Parser(url).parse()


_POSSIBLE_REGEXES = (
    re.compile(r'^(?P<protocol>https?|git|ssh|rsync)\://'
               r'(?:(?P<user>.+)@)*'
               r'(?P<resource>[a-z0-9_.-]*)'
               r'[:/]*'
               r'(?P<port>[\d]+){0,1}'
               r'(?P<pathname>\/([\w\-]+\/)?'
               r'([\w.-]+?(\.git|\/)?)?)$'),
    re.compile(r'(git\+)?'
               r'((?P<protocol>\w+)://)'
               r'((?P<user>\w+)@)?'
               r'((?P<resource>[\w\.\-]+))'
               r'(:(?P<port>\d+))?'
               r'(?P<pathname>(\/\w+/)?'
               r'(\/?[\w.-]+(\.git|\/)?)?)$'),
    re.compile(r'^(?:(?P<user>.+)@)*'
               r'(?P<resource>[a-z0-9_.-]*)[:]*'
               r'(?P<port>[\d]+){0,1}'
               r'(?P<pathname>\/?.+/.+\.git)$'),
    re.compile(r'((?P<user>\w+)@)?'
               r'((?P<resource>[\w\.\-]+))'
               r'[\:\/]{1,2}'
               r'(?P<pathname>(\w+/)?'
               r'([\w.-]+(\.git|\/)?)?)$'),
)


class ParserError(Exception):
    """Error raised when a URL can't be parsed."""


class _Parser:
    """A class responsible for parsing a GIT URL and return a `Parsed` object."""

    def __init__(self, url):
        self._url = url

    def parse(self) -> Parsed:
        """Parses a GIT URL and returns an object.

        Raises an exception on invalid URL.

        :returns: Parsed object
        :raise: :class:`.ParserError`
        """
        kwargs = {
            'pathname': None,
            'protocols': self._get_protocols(),
            'protocol': 'ssh',
            'href': self._url,
            'resource': None,
            'user': None,
            'port': None,
        }
        for regex in _POSSIBLE_REGEXES:
            match = regex.search(self._url)
            if match:
                kwargs.update(match.groupdict())
                break
        else:
            raise ParserError(f"Invalid URL '{self._url}'")
        return Parsed(**kwargs)

    def _get_protocols(self) -> List[str]:
        try:
            index = self._url.index('://')
            return self._url[:index].split('+')
        except ValueError:
            return []
