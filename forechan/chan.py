from asyncio import sleep
from asyncio.locks import Event
from collections import deque
from contextlib import contextmanager
from typing import Any, AsyncIterator, Deque, Iterator, Optional, Type, TypeVar, cast

from .types import Chan, ChanClosed, ChanEmpty, ChanFull

T = TypeVar("T")


class _Chan(Chan[T], AsyncIterator[T]):
    def __init__(self, maxlen: int) -> None:
        super().__init__()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))
        self._sendable, self._recvable = Event(), Event()
        self._onclose = Event()
        self._sendable.set()

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __str__(self) -> str:
        if self:
            return f"chan[{', '.join(str(item) for item in self._q)}]"
        else:
            return "chan|<closed>|"

    def __bool__(self) -> bool:
        return not self._onclose.is_set()

    def __len__(self) -> int:
        return len(self._q)

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

    def empty(self) -> bool:
        if not self:
            raise ChanClosed()
        else:
            return not len(self)

    def full(self) -> bool:
        if not self:
            raise ChanClosed()
        else:
            return len(self) >= self.maxlen

    async def close(self) -> None:
        await sleep(0)
        self._q.clear()
        self._onclose.set()
        self._sendable.set()
        self._recvable.set()

    @contextmanager
    def _state_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            try:
                if self.empty():
                    self._recvable.clear()
                else:
                    self._recvable.set()

                if self.full():
                    self._sendable.clear()
                else:
                    self._sendable.set()
            except ChanClosed:
                pass

    def try_peek(self) -> T:
        if self.empty():
            raise ChanEmpty()
        else:
            return next(iter(self._q))

    def try_send(self, item: T) -> None:
        if self.full():
            raise ChanFull()
        else:
            with self._state_handler():
                self._q.append(item)

    async def send(self, item: T) -> None:
        while True:
            if self.full():
                await self._sendable.wait()
            else:
                with self._state_handler():
                    return self._q.append(item)

    def try_recv(self) -> T:
        if self.empty():
            raise ChanEmpty()
        else:
            with self._state_handler():
                return self._q.popleft()

    async def recv(self) -> T:
        while True:
            if self.empty():
                await self._recvable.wait()
            else:
                with self._state_handler():
                    return self._q.popleft()

    async def _closed_notif(self) -> None:
        await self._onclose.wait()

    async def _sendable_notif(self) -> None:
        await self._sendable.wait()
        if not self:
            raise ChanClosed()

    async def _recvable_notif(self) -> None:
        await self._recvable.wait()
        if not self:
            raise ChanClosed()


def chan(t: Optional[Type[T]] = None, maxlen: int = 1) -> Chan[T]:
    return _Chan[T](maxlen=maxlen)
