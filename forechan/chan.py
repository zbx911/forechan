from abc import abstractmethod
from asyncio import sleep
from asyncio.locks import Event
from contextlib import contextmanager
from typing import Any, AsyncIterator, Iterator, Optional, Type, TypeVar

from .bufs import NormalBuf
from .types import Buf, Chan, ChanClosed, ChanEmpty, ChanFull

T = TypeVar("T")


class _BaseChan(Chan[T], AsyncIterator[T]):
    _b: Buf[T]

    def __str__(self) -> str:
        if self:
            return f"chan[{', '.join(str(item) for item in self._b)}]"
        else:
            return "chan|<closed>|"

    def __len__(self) -> int:
        return len(self._b)

    async def __aenter__(self) -> Chan[T]:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        try:
            return await self.recv()
        except ChanClosed:
            raise StopAsyncIteration()

    def __lt__(self, item: T) -> None:
        self.try_send(item)

    def __gt__(self, _: Any) -> T:
        return self.try_recv()

    async def __lshift__(self, item: T) -> None:
        await self.send(item)

    async def __rlshift__(self, _: Any) -> T:
        return await self.recv()

    def sendable(self) -> bool:
        return bool(self) and not self._b.full()

    def recvable(self) -> bool:
        return bool(self) and not self._b.empty()


class _Chan(_BaseChan[T]):
    def __init__(self, b: Buf[T]) -> None:
        self._b: Buf[T] = b
        self._sendable_ev, self._recvable_ev = Event(), Event()
        self._onclose = Event()
        self._sendable_ev.set()

    def __bool__(self) -> bool:
        return not self._onclose.is_set()

    async def close(self) -> None:
        await sleep(0)
        self._b.close()
        self._onclose.set()
        self._sendable_ev.set()
        self._recvable_ev.set()

    @contextmanager
    def _state_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            if self.sendable():
                self._sendable_ev.set()
            else:
                self._sendable_ev.clear()

            if self.recvable():
                self._recvable_ev.set()
            else:
                self._recvable_ev.clear()

    def try_peek(self) -> T:
        if not self:
            raise ChanClosed()
        elif not self.recvable():
            raise ChanEmpty()
        else:
            return next(iter(self._b))

    def try_send(self, item: T) -> None:
        if not self:
            raise ChanClosed()
        elif not self.sendable():
            raise ChanFull()
        else:
            with self._state_handler():
                self._b.send(item)

    async def send(self, item: T) -> None:
        while self:
            if not self.sendable():
                await self._sendable_ev.wait()
            else:
                with self._state_handler():
                    return self._b.send(item)
        else:
            raise ChanClosed()

    def try_recv(self) -> T:
        if not self:
            raise ChanClosed()
        elif not self.recvable():
            raise ChanEmpty()
        else:
            with self._state_handler():
                return self._b.recv()

    async def recv(self) -> T:
        while self:
            if not self.recvable():
                await self._recvable_ev.wait()
            else:
                with self._state_handler():
                    return self._b.recv()
        else:
            raise ChanClosed()

    async def _on_closed(self) -> Chan[T]:
        await self._onclose.wait()
        return self

    async def _on_sendable(self) -> Chan[T]:
        await self._sendable_ev.wait()
        return self

    async def _on_recvable(self) -> Chan[T]:
        await self._recvable_ev.wait()
        return self


def chan(t: Optional[Type[T]] = None, buf: Optional[Buf[T]] = None) -> Chan[T]:
    b = buf or NormalBuf[T](maxlen=1)
    return _Chan[T](b=b)
