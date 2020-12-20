from asyncio.tasks import gather
from typing import Callable, TypeVar

from .chan import chan
from .go import go
from .types import Chan

T = TypeVar("T")


async def sub(predicate: Callable[[T], bool], pub: Chan[T]) -> Chan[T]:
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            while pub and out:
                await gather(pub._on_recvable(), out._on_sendable())
                if pub.recvable() and out.sendable():
                    item = pub.try_peek()
                    if predicate(item):
                        out.try_send(pub.try_recv())

    await go(cont())
    return out
