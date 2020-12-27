from asyncio.locks import Event
from asyncio.tasks import create_task
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    MutableMapping,
    Protocol,
    TypeVar,
    cast,
    runtime_checkable,
)
from itertools import chain

from ._da import race
from .types import Chan, Closable

T = TypeVar("T")

Sender = Callable[[], T]
Recver = Callable[[T], None]


@runtime_checkable
class Selector(Closable, AsyncContextManager["Selector"], Protocol):
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
        self._on_closed = Event()
        self._sc: MutableMapping[Chan[Any], Sender[Any]] = {}
        self._rc: MutableMapping[Chan[Any], Recver[Any]] = {}

    def __bool__(self) -> bool:
        return not self._on_closed.is_set()

    async def __aexit__(self, *_: Any) -> None:
        while not self._on_closed.is_set() and (self._sc or self._rc):
            ch, _ = await race(
                *(
                    create_task(aw)
                    for aw in chain(
                        (self._on_closed.wait(),),
                        (ch._on_sendable() for ch in self._sc),
                        (ch._on_recvable() for ch in self._rc),
                    )
                )
            )
            if ch == True:
                break
            else:
                ch = cast(Chan[Any], ch)
                if not ch:
                    self._sc = {c: f for c, f in self._sc.items()}
                    self._rc = {c: f for c, f in self._rc.items()}
                elif ch in self._sc:
                    if ch.sendable():
                        ch.try_send(self._sc[ch]())
                elif ch in self._rc:
                    if ch.recvable():
                        self._rc[ch](ch.try_recv())
                else:
                    assert False

    def close(self) -> None:
        self._on_closed.set()

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


async def selector() -> Selector:
    """
    special `select` to support sendable chan

    see doc for `Selector`
    """
    s = _Selector()
    return s
