from asyncio.locks import Event, Lock
from asyncio.tasks import gather
from collections import deque
from contextlib import contextmanager
from typing import Any, AsyncIterator, Deque, Iterator, Optional, Type, TypeVar, cast

from .types import Chan, ChanClosed

T = TypeVar("T")


class _Chan(Chan[T], AsyncIterator[T]):
    def __init__(self, maxlen: int) -> None:
        super().__init__()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))
        self._sendlock, self._recvlock = Lock(), Lock()
        self._sendable, self._recvable = Event(), Event()
        self._onclose = Event()
        self._sendable.set()

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def __str__(self) -> str:
        return f"chan[{', '.join(str(item) for item in self._q)}]"

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
        self._q.clear()
        self._onclose.set()
        self._sendable.set()
        self._recvable.set()

    @contextmanager
    def _state_handler(self) -> Iterator[None]:
        try:
            yield None
        finally:
            if self.empty():
                self._recvable.clear()
            else:
                self._recvable.set()

            if self.full():
                self._sendable.clear()
            else:
                self._sendable.set()

    async def send(self, item: T) -> None:
        with self._state_handler():
            while self.full():
                await self._sendable.wait()

            async with self._sendlock:
                if not self:
                    raise ChanClosed()
                else:
                    self._q.append(item)

    async def recv(self) -> T:
        with self._state_handler():
            while self.empty():
                await self._recvable.wait()

            async with self._recvlock:
                if not self:
                    raise ChanClosed()
                else:
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
