from abc import abstractmethod
from collections import deque
from typing import (
    Callable,
    Deque,
    Generic,
    Iterator, List,
    MutableSequence,
    Sized,
    TypeVar,
    cast,
)
from heapq import heappop, heappush

from .types import Buf

T = TypeVar("T")


class _AbsBuf(Sized, Generic[T]):
    @property
    @abstractmethod
    def _q(self) -> MutableSequence[T]:
        ...

    def __len__(self) -> int:
        return len(self._q)

    def __iter__(self) -> Iterator[T]:
        return iter(self._q)

    def close(self) -> None:
        self._q.clear()


class NormalBuf(_AbsBuf[T], Buf[T]):
    def __init__(self, maxlen: int) -> None:
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

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


class PiorityBuf(_AbsBuf[T], Buf[T]):
    def __init__(self, determinate: Callable[[T], int], maxlen: int) -> None:
        self._ml = maxlen
        self._det = determinate
        self._q: List[T] = []

    @property
    def maxlen(self) -> int:
        return self._ml

    def send(self, item: T) -> None:
        heappush(self._q, item)

    def recv(self) -> T:
        return heappop(self._q)