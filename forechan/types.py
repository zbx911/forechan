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


class Clearable(Protocol):
    @abstractmethod
    def clear(self) -> None:
        """
        idempotent
        """


class AsyncClosable(Protocol):
    @abstractmethod
    async def close(self) -> None:
        """
        idempotent
        """


@runtime_checkable
class Chan(Sized, AsyncClosable, AsyncContextManager, AsyncIterable[T], Protocol[T]):
    """
    CSP channels
    <NOT thread safe>!
    """

    @abstractmethod
    def __bool__(self) -> bool:
        """
        # check if `ch` is open / closed
        if ch:
            ...
        """

    @abstractmethod
    async def __aenter__(self) -> Chan[T]:
        """
        # close `ch` on block exit
        async with ch:
            ...
        """

    @abstractmethod
    async def __anext__(self) -> T:
        """
        close `ch` on exit
        """

    @abstractmethod
    def __lt__(self, item: T) -> None:
        """
        # try_send:
        (ch < 123)
        """

    @abstractmethod
    def __gt__(self, _: Any) -> T:
        """
        # try_recv:
        item = ([] < ch)
        """

    @abstractmethod
    async def __lshift__(self, item: T) -> None:
        """
        # send:
        await (ch << 123)
        """

    @abstractmethod
    async def __rlshift__(self, _: Any) -> T:
        """
        # recv:
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
class Buf(Sized, Clearable, Iterable[T], Protocol[T]):
    """
    bufs customize chan behaviour
    <implementation should not throw errors>!
    """

    @abstractmethod
    def empty(self) -> bool:
        """
        chan will block on recv if `empty()`
        """

    @abstractmethod
    def full(self) -> bool:
        """
        chan will block on send if `full()`
        """

    @abstractmethod
    def push(self, item: T) -> None:
        ...

    @abstractmethod
    def pop(self) -> T:
        ...


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
