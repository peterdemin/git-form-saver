import asyncio
from multidict import MultiDict


def run(future):
    return asyncio.new_event_loop().run_until_complete(future)


class FakeRequest:
    def __init__(self, result: dict, headers: dict = None) -> None:
        self._result = MultiDict(result)
        self.headers = headers or {'Referer': 'Referer'}

    async def post(self) -> MultiDict:
        return self._result
