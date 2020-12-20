from __future__ import annotations

from typing import Any, AsyncContextManager, Callable, MutableMapping, Protocol, TypeVar

from ._da import race
from .go import GO, go
from .ops import with_aclosing
from .types import Chan

T = TypeVar("T")


class Selector(AsyncContextManager["Selector"], Protocol):
    def on_sendable(
        self,
        ch: Chan[T],
    ) -> Callable[[Callable[[], T]], Callable[[], T]]:
        ...

    def on_recvable(
        self,
        ch: Chan[T],
    ) -> Callable[[Callable[[T], None]], Callable[[T], None]]:
        ...


class _Selector(Selector):
    def __init__(self, cascade_close: bool, go: GO) -> None:
        self._cc = cascade_close
        self._go = go
        self._sc: MutableMapping[Chan[Any], Callable[[], Any]] = {}
        self._rc: MutableMapping[Chan[Any], Callable[[Any], None]] = {}

    async def __aexit__(self, *_: Any) -> None:
        async def cont() -> None:
            async with with_aclosing(*self._sc, *self._rc, close=self._cc):
                while self._sc and self._rc:
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

        await self._go(cont())

    def on_sendable(
        self,
        ch: Chan[T],
    ) -> Callable[[Callable[[], T]], Callable[[], T]]:
        def decor(closure: Callable[[], T]) -> Callable[[], T]:
            self._sc[ch] = closure
            return closure

        return decor

    def on_recvable(
        self,
        ch: Chan[T],
    ) -> Callable[[Callable[[T], None]], Callable[[T], None]]:
        def decor(closure: Callable[[T], None]) -> Callable[[T], None]:
            self._rc[ch] = closure
            return closure

        return decor


async def selector(cascade_close: bool = True, go: GO = go) -> Selector:
    s = _Selector(cascade_close=cascade_close, go=go)
    return s
