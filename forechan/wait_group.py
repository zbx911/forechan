from abc import abstractmethod
from asyncio import sleep
from asyncio.locks import Event
from typing import Any, ContextManager, Protocol, Sized, runtime_checkable


@runtime_checkable
class WaitGroup(Sized, ContextManager[None], Protocol):
    """
    wg = wait_group()

    # this is a `wg` block
    with wg:
        ...
    """

    @abstractmethod
    async def wait(self) -> None:
        """
        # wait for all `wg` blocks to exit

        await wg.wait()
        """


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
    """
    wg = wait_group()

    for _ in range(5):
        async def cont() -> None:
            with wg:
                # do some work

        await go(cont())

    # will wait for all work to be completed
    await wg.wait()
    """

    return _WaitGroup()
