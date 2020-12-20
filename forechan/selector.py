from asyncio.locks import Event
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

from ._da import race
from .go import GO, go
from .ops import with_aclosing
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
    def __init__(self, cascade_close: bool, go: GO) -> None:
        self._on_closed = Event()
        self._cc = cascade_close
        self._go = go
        self._sc: MutableMapping[Chan[Any], Sender[Any]] = {}
        self._rc: MutableMapping[Chan[Any], Recver[Any]] = {}

    async def __aexit__(self, *_: Any) -> None:
        async def cont() -> None:
            async with with_aclosing(*self._sc, *self._rc, close=self._cc):
                while not self._on_closed.is_set() and (self._sc or self._rc):
                    ch, _ = await race(
                        self._on_closed.wait(),
                        *(ch._on_sendable() for ch in self._sc),
                        *(ch._on_recvable() for ch in self._rc)
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

        await (await self._go(cont()))

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


async def selector(cascade_close: bool = True, go: GO = go) -> Selector:
    """
    special `select` to support sendable chan

    see doc for `Selector`
    """
    s = _Selector(cascade_close=cascade_close, go=go)
    return s
