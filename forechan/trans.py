from typing import AsyncIterator, Callable, Deque, Generic, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")


def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
) -> Chan[U]:
    out: Chan[U] = chan()

    return out