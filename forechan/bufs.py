from collections import deque
from typing import Deque, Generic, Iterator, MutableSequence, Sized, TypeVar, cast

from .types import Buf, Closable

T = TypeVar("T")


class _BaseBuf(Sized, Closable, Generic[T]):
    _q: MutableSequence[T]

    def __len__(self) -> int:
        return len(self._q)

    def __iter__(self) -> Iterator[T]:
        return iter(self._q)

    def empty(self) -> bool:
        return not len(self)

    def close(self) -> None:
        self._q.clear()


class NormalBuf(_BaseBuf[T], Buf[T]):
    """
    When at capacity, block
    """

    def __init__(self, maxlen: int) -> None:
        self._q: Deque[T] = deque(maxlen=max(1, maxlen))

    @property
    def maxlen(self) -> int:
        return cast(int, self._q.maxlen)

    def full(self) -> bool:
        return len(self) >= self.maxlen

    def send(self, item: T) -> None:
        self._q.append(item)

    def recv(self) -> T:
        return self._q.popleft()


class SlidingBuf(NormalBuf[T]):
    """
    When at capacity, dispose earliest messages
    """

    def full(self) -> bool:
        return False


class DroppingBuf(NormalBuf[T]):
    """
    When at capacity, dispose latest messages
    """

    def full(self) -> bool:
        return False

    def send(self, item: T) -> None:
        if len(self) < self.maxlen:
            self._q.append(item)
