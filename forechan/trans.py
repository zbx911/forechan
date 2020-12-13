from typing import AsyncIterator, Callable, Deque, Generic, TypeVar

from .types import Channel, ChannelClosed

T = TypeVar("T")
U = TypeVar("U")


def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    chan: Channel[T],
) -> Channel[U]:
    pass
