from asyncio.tasks import create_task
from typing import Any, AsyncIterator, Callable, Tuple, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")


async def select(ch: Chan[Any], *chs: Chan[Any]) -> AsyncIterator[Tuple[Chan, Any]]:
    pass


async def trans(
    trans: Callable[[AsyncIterator[T]], AsyncIterator[U]],
    ch: Chan[T],
) -> Chan[U]:
    out: Chan[U] = chan()

    async def cont() -> None:
        async with out:
            async for item in trans(ch):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out


async def fan_in(ch: Chan[T], *chs: Chan[T]) -> Chan[T]:
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            async for _, item in select(ch, *chs):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out


# def fan_out(ch: Chan[T])
