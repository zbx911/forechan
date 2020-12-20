from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterable,
    ContextManager,
    Iterable,
    Protocol,
    Sized,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")


class ChanClosed(Exception):
    ...


class ChanEmpty(Exception):
    ...


class ChanFull(Exception):
    ...


class Boolable(Protocol):
    @abstractmethod
    def __bool__(self) -> bool:
        ...


class Closable(Protocol):
    @abstractmethod
    def close(self) -> None:
        ...


class AsyncClosable(Protocol):
    @abstractmethod
    async def close(self) -> None:
        ...


@runtime_checkable
class Chan(
    Sized, Boolable, AsyncClosable, AsyncContextManager, AsyncIterable[T], Protocol[T]
):
    """
    check if `ch` is open:
    bool(ch), if ch:

    check `ch` len:
    len(ch)
    """

    @abstractmethod
    async def __aenter__(self) -> Chan[T]:
        """
        async with ch:
            ...
        """

    @abstractmethod
    async def __anext__(self) -> T:
        """
        close Chan[T] on exit
        """

    @abstractmethod
    def __lt__(self, item: T) -> None:
        """
        try_send:
        (ch < 123)
        """

    @abstractmethod
    def __gt__(self, _: Any) -> T:
        """
        try_recv:
        item = ([] < ch)
        """

    @abstractmethod
    async def __lshift__(self, item: T) -> None:
        """
        send:
        await (ch << 123)
        """

    @abstractmethod
    async def __rlshift__(self, _: Any) -> T:
        """
        recv:
        item = await ([] << ch)
        """

    @abstractmethod
    def sendable(self) -> bool:
        ...

    @abstractmethod
    def recvable(self) -> bool:
        ...

    @abstractmethod
    async def _on_closed(self) -> Chan[T]:
        """
        returns immediately when chan is closed
        """

    @abstractmethod
    def try_peek(self) -> T:
        """
        can throw ChanEmpty, ChanClosed
        """

    @abstractmethod
    def try_send(self, item: T) -> None:
        """
        can throw ChanFull, ChanClosed
        """

    @abstractmethod
    async def send(self, item: T) -> None:
        """
        can throw ChanClosed
        """

    @abstractmethod
    async def _on_sendable(self) -> Chan[T]:
        """
        returns immediately when chan is closed
        """

    @abstractmethod
    def try_recv(self) -> T:
        """
        can throw ChanEmpty, ChanClosed
        """

    @abstractmethod
    async def recv(self) -> T:
        """
        can throw ChanClosed
        """

    @abstractmethod
    async def _on_recvable(self) -> Chan[T]:
        """
        returns immediately when chan is closed
        """


@runtime_checkable
class Buf(Sized, Closable, Iterable[T], Protocol[T]):
    @abstractmethod
    def empty(self) -> bool:
        ...

    @abstractmethod
    def full(self) -> bool:
        ...

    @abstractmethod
    def send(self, item: T) -> None:
        ...

    @abstractmethod
    def recv(self) -> T:
        ...


@runtime_checkable
class WaitGroup(Sized, ContextManager[None], Protocol):
    """
    for _ in range(10):
        async def f():
            with wg:
                ...
        create_task(f())

    await wg.wait() # all tasks finish
    """

    @abstractmethod
    async def wait(self) -> None:
        ...
