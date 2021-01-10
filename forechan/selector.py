from asyncio.tasks import create_task
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    MutableMapping,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from ._da import race
from .types import Chan

T = TypeVar("T")

Sender = Callable[[], T]
Recver = Callable[[T], None]


class StopSelector(Exception):
    ...


@runtime_checkable
class Selector(AsyncContextManager["Selector"], Protocol):
    """
    async with selector() as sr:
        @sr.on_sendable(ch)
        def f1():
            ...
            return item

        @sr.on_recvable(ch)
        def f1(item):
            ...
    """

    def on_sendable(
        self,
        ch: Chan[T],
    ) -> Callable[[Sender[T]], Sender[T]]:
        """
        register closure to be called on send
        """

    def on_recvable(
        self,
        ch: Chan[T],
    ) -> Callable[[Recver[T]], Recver[T]]:
        """
        register closure to be called on recv
        """


class _Selector(Selector):
    def __init__(self) -> None:
        self._sc: MutableMapping[Chan[Any], Sender[Any]] = {}
        self._rc: MutableMapping[Chan[Any], Recver[Any]] = {}

    async def __aexit__(self, *_: Any) -> None:
        while self._sc or self._rc:
            _ch, __, __ = await race(
                *(create_task(ch._on_sendable()) for ch in self._sc),
                *(create_task(ch._on_recvable()) for ch in self._rc),
            )
            ch = _ch.result()

            if not ch:
                self._sc = {c: f for c, f in self._sc.items()}
                self._rc = {c: f for c, f in self._rc.items()}
            elif ch in self._sc:
                if ch.sendable():
                    try:
                        ch.try_send(self._sc[ch]())
                    except StopSelector:
                        break
            elif ch in self._rc:
                if ch.recvable():
                    try:
                        self._rc[ch](ch.try_recv())
                    except StopSelector:
                        break
            else:
                assert False

    def on_sendable(
        self,
        ch: Chan[T],
    ) -> Callable[[Sender[T]], Sender[T]]:
        def decor(closure: Sender[T]) -> Sender:
            self._sc[ch] = closure
            return closure

        return decor

    def on_recvable(
        self,
        ch: Chan[T],
    ) -> Callable[[Recver[T]], Recver[T]]:
        def decor(closure: Recver[T]) -> Recver[T]:
            self._rc[ch] = closure
            return closure

        return decor


def selector() -> Selector:
    """
    special `select` to support sendable chan

    see doc for `Selector`
    """

    return _Selector()
