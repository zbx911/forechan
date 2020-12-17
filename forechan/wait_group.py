from asyncio import sleep
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
        self._event.clear()

    def __exit__(self, *_: Any) -> None:
        self._counter -= 1

        if self._counter < 0:
            raise ValueError()
        elif len(self) == 0:
            self._event.set()

    async def wait(self) -> None:
        await sleep(0)
        if len(self):
            await self._event.wait()


def wait_group() -> WaitGroup:
    return _WaitGroup()
