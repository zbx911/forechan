from asyncio.tasks import create_task, gather
from typing import MutableSequence, TypeVar

from .ops import with_closing
from .types import Chan
from ._da import race

T = TypeVar("T")


async def distribute(src: Chan[T], *dest: Chan[T], cascade_close: bool = True) -> None:
    cs: MutableSequence[Chan[T]] = [*dest]

    async def cont() -> None:
        async with with_closing(src, *dest, close=cascade_close):
            while src and cs:
                _, (ready, _) = await gather(
                    src._on_recvable(),
                    race(*(ch._on_sendable() for ch in cs)),
                )
                if not ready:
                    cs[:] = [ch for ch in cs if ch]
                elif src.recvable() and ready.sendable():
                    ready.try_send(src.try_recv())

    create_task(cont())