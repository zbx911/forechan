from asyncio.tasks import gather
from contextlib import asynccontextmanager
from typing import AsyncIterable, AsyncIterator, Iterable, TypeVar, Union, cast

from .types import AsyncClosable, Chan

T = TypeVar("T")


async def to_chan(it: Union[Iterable[T], AsyncIterable[T]], ch: Chan[T]) -> None:
    """
    Iterable[T] / AsyncIterable[T] -> Chan[T]
    """

    async def gen() -> AsyncIterator[T]:
        for item in cast(Iterable[T], it):
            yield item

    ait = gen() if isinstance(it, Iterable) else it
    async with ch:
        async for item in ait:
            while ch:
                await ch._on_sendable()
                if ch.sendable():
                    ch.try_send(item)
                    break
            if not ch:
                break


@asynccontextmanager
async def with_aclosing(*closables: AsyncClosable) -> AsyncIterator[None]:
    """
    async with with_closing(*cs):
        ...
    # close each `chan` in *cs after block
    """

    try:
        yield None
    finally:
        await gather(*(c.aclose() for c in closables))
