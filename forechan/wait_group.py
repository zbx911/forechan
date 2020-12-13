from asyncio.locks import Event
from typing import Any

from .types import WaitGroup


class _WaitGroup(WaitGroup):
    def __init__(self) -> None:
        self._counter = 0
        self._event = Event()

    def __len__(self) -> int:
        return self._counter

    def __enter__(self) -> None:
        self._counter += 1

    def __exit__(self, *_: Any) -> None:
        self._counter -= 1
        if not len(self):
            self._event.set()
        elif self._counter < 0:
            raise ValueError()

    async def wait(self) -> None:
        if len(self):
            await self._event.wait()


def wait_group() -> WaitGroup:
    return _WaitGroup()
