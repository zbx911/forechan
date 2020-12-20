from typing import Any, AsyncContextManager, Callable, MutableMapping, Protocol, TypeVar

from ._da import race
from .go import GO, go
from .ops import with_aclosing
from .types import Chan, Closable

T = TypeVar("T")

Sender = Callable[[], T]
Recver = Callable[[T], None]


class Selector(Closable, AsyncContextManager["Selector"], Protocol):
    def on_sendable(
        self,
        ch: Chan[T],
    ) -> Callable[[Sender[T]], Sender[T]]:
        ...

    def on_recvable(
        self,
        ch: Chan[T],
    ) -> Callable[[Recver[T]], Recver[T]]:
        ...


class _Selector(Selector):
    def __init__(self, cascade_close: bool, go: GO) -> None:
        self._closed = False
        self._cc = cascade_close
        self._go = go
        self._sc: MutableMapping[Chan[Any], Sender[Any]] = {}
        self._rc: MutableMapping[Chan[Any], Recver[Any]] = {}

    async def __aexit__(self, *_: Any) -> None:
        async def cont() -> None:
            async with with_aclosing(*self._sc, *self._rc, close=self._cc):
                while not self._closed and (self._sc or self._rc):
                    ch, _ = await race(
                        *(ch._on_sendable() for ch in self._sc),
                        *(ch._on_recvable() for ch in self._rc)
                    )

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
        self._closed = True

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
    s = _Selector(cascade_close=cascade_close, go=go)
    return s
