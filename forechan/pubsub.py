from asyncio.tasks import gather
from typing import Callable, TypeVar

from .types import Chan

T = TypeVar("T")


async def sub(predicate: Callable[[T], bool], pub: Chan[T], sub: Chan[T]) -> None:
    while pub and sub:
        await gather(pub._on_recvable(), sub._on_sendable())
        if pub.recvable() and sub.sendable():
            if predicate(pub.try_peek()):
                sub.try_send(pub.try_recv())
