from asyncio import FIRST_COMPLETED, wait
from asyncio.futures import Future
from asyncio.tasks import gather
from collections import deque
from itertools import chain
from typing import Awaitable, Deque, Set, Sized, Tuple, TypeVar, cast

from .types import Channel

T = TypeVar("T")
U = TypeVar("U")


def join(chan: Channel[T], *chans: Channel[T]) -> Channel[T]:
    pass