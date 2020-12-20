from typing import Optional, Type, TypeVar

from .chan import chan
from .types import Buf, Chan
from .bufs import _BaseBuf

T = TypeVar("T")


class _BroadcastBuf(_BaseBuf[T], Buf[T]):
    def __init__(self) -> None:
        self._q = []

    def full(self) -> bool:
        return False

    def push(self, item: T) -> None:
        self.clear()
        self._q.append(item)

    def pop(self) -> T:
        return next(iter(self._q))


def broadcast(t: Optional[Type[T]]) -> Chan[T]:
    return chan(t, buf=_BroadcastBuf[T]())
