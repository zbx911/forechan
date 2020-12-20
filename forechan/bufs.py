from collections import deque
from typing import Deque, Generic, Iterator, MutableSequence, Sized, TypeVar

from .types import Buf, Clearable

T = TypeVar("T")


class _BaseBuf(Sized, Clearable, Generic[T]):
    _q: MutableSequence[T]

    def __len__(self) -> int:
        return len(self._q)

    def __iter__(self) -> Iterator[T]:
        return iter(self._q)

    def empty(self) -> bool:
        return not len(self)

    def clear(self) -> None:
        self._q.clear()


class NormalBuf(_BaseBuf[T], Buf[T]):
    """
    When at capacity, block
    """

    def __init__(self, maxlen: int) -> None:
        self._q: Deque[T] = deque()
        self._maxlen = maxlen

    def full(self) -> bool:
        return len(self) >= self._maxlen

    def push(self, item: T) -> None:
        self._q.append(item)

    def pop(self) -> T:
        return self._q.popleft()


class SlidingBuf(NormalBuf[T]):
    """
    When at capacity, dispose earliest messages
    """

    def full(self) -> bool:
        return False

    def push(self, item: T) -> None:
        if len(self) >= self._maxlen:
            self._q.popleft()
            self._q.append(item)


class DroppingBuf(NormalBuf[T]):
    """
    When at capacity, dispose latest messages
    """

    def full(self) -> bool:
        return False

    def push(self, item: T) -> None:
        if len(self) < self._maxlen:
            self._q.append(item)
