from collections import deque
from typing import Deque, Iterator, TypeVar, cast

from .types import Buffer

T = TypeVar("T")


class NormalBuf(Buffer[T]):
    def __init__(self, maxlen: int) -> None:
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))

    def __len__(self) -> int:
        return len(self._q)

    def __iter__(self) -> Iterator[T]:
        return iter(self._q)

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def close(self) -> None:
        self._q.clear()

    def send(self, item: T) -> None:
        self._q.append(item)

    def recv(self) -> T:
        return self._q.popleft()


class SlidingBuf(NormalBuf[T]):
    def send(self, item: T) -> None:
        if len(self) < self.maxlen:
            self._q.append(item)


class DroppingBuf(NormalBuf[T]):
    def send(self, item: T) -> None:
        if len(self) >= self.maxlen:
            self._q.popleft()
            self._q.append(item)
