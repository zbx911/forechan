from asyncio.tasks import create_task, gather
from contextlib import asynccontextmanager
from typing import Any, AsyncIterable, AsyncIterator, Iterable, TypeVar, Union, cast

from .chan import chan
from .types import AsyncClosable, Chan, ChanClosed
from .wait_group import wait_group

T = TypeVar("T")


async def to_chan(it: Union[Iterable[T], AsyncIterable[T]]) -> Chan[T]:
    ch: Chan[T] = chan()

    async def gen() -> AsyncIterator[T]:
        for item in cast(Iterable[T], it):
            yield item

    ait = gen() if isinstance(it, Iterable) else it

    async def cont() -> None:
        async with ch:
            async for item in ait:
                try:
                    await ch.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return ch


async def cascading_close(src: Iterable[Chan[Any]], dest: Iterable[Chan[Any]]) -> None:
    wg = wait_group()
    for ch in src:

        async def cont() -> None:
            with wg:
                await ch._on_closed()

        create_task(cont())

    async def close() -> None:
        await wg.wait()
        await gather(*(ch.close() for ch in dest))

    create_task(close())


@asynccontextmanager
async def with_closing(
    *closables: AsyncClosable, close: bool = True
) -> AsyncIterator[None]:
    try:
        yield None
    finally:
        if close:
            await gather(*(c.close() for c in closables))
