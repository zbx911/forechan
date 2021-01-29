from abc import abstractmethod
from asyncio import sleep
from asyncio.locks import Event
from types import TracebackType
from typing import (
    ContextManager,
    Literal,
    Optional,
    Protocol,
    Sized,
    Type,
    runtime_checkable,
)

from .types import Boolable


@runtime_checkable
class WaitGroup(Sized, Boolable, ContextManager[None], Protocol):
    """
    wg = wait_group()

    # this is a `wg` block
    # Note, wg will capture and propagate Exceptions
    with wg:
        ...
    """

    @abstractmethod
    def maybe_throw() -> None:
        """
        Throw exceptions, if any
        """

    @abstractmethod
    async def wait(self) -> None:
        """
        # wait for all `wg` blocks to exit
        # propagates exceptions

        await wg.wait()
        """


class _WaitGroup(WaitGroup):
    def __init__(self) -> None:
        self._counter = 0
        self._event = Event()
        self._err: Optional[BaseException] = None

    def __bool__(self) -> bool:
        return not self._event.is_set()

    def __len__(self) -> int:
        return self._counter

    def __enter__(self) -> None:
        self._counter += 1
        self._event.clear()

    def __exit__(
        self,
        _: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[True]:
        if self._err is not None:
            pass
        elif exc_value is not None:
            self._err = exc_value
            self._event.set()
        else:
            self._counter -= 1
            if self._counter < 0:
                raise RuntimeError()
            elif len(self) == 0:
                self._event.set()

        return True

    def maybe_throw(self) -> None:
        if self._err is not None:
            raise self._err

    async def wait(self) -> None:
        await sleep(0)
        if len(self):
            await self._event.wait()
            if self._err is not None:
                raise self._err


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
