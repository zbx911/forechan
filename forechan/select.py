from asyncio import gather
from collections import deque
from typing import Any, Deque, Sequence, Tuple, TypeVar, cast

from .types import Channel, ChannelClosed

T = TypeVar("T")


def select(
    chan: Channel[Any], *chans: Channel[Any]
) -> Channel[Tuple[Channel[Any], Any]]:
    pass
