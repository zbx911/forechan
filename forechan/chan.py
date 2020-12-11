from asyncio.locks import Condition
from collections import deque
from math import inf
from typing import Deque, TypeVar

from ._base import BaseChan
from .types import ChannelClosed

T = TypeVar("T")


class Chan(BaseChan[T]):
    def __init__(self, maxlen: int = 1) -> None:
        self._closed = False
        self._send_cond = Condition()
        self._recv_cond = Condition()
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))

    def __bool__(self) -> bool:
        return not self._closed

    def __len__(self) -> int:
        if self:
            return len(self._q)
        else:
            return 0

    async def close(self) -> None:
        self._closed = True
        async with self._send_cond:
            self._send_cond.notify_all()
        async with self._recv_cond:
            self._recv_cond.notify_all()

    async def send(self, item: T) -> None:
        if not self:
            raise ChannelClosed()
        elif len(self) < (self._q.maxlen or inf):
            self._q.append(item)
            self._recv_cond.notify()
        else:
            async with self._send_cond:
                await self._send_cond.wait()
                if not self:
                    raise ChannelClosed()
                else:
                    self._q.append(item)
                    self._recv_cond.notify()

    async def recv(self) -> T:
        if not self:
            raise ChannelClosed()
        elif len(self):
            self._send_cond.notify()
            return self._q.popleft()
        else:
            async with self._recv_cond:
                await self._recv_cond.wait()
                if not self:
                    raise ChannelClosed()
                else:
                    self._send_cond.notify()
                    return self._q.popleft()
