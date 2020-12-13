from asyncio.locks import BoundedSemaphore
from asyncio.tasks import create_task
from typing import Any, AsyncIterator, Callable, Sequence, Tuple, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")


async def select(ch: Chan[Any], *chs: Chan[Any]) -> Chan[Tuple[Chan, Any]]:
    out: Chan[Any] = chan()
    channels: Sequence[Chan[Any]] = tuple((ch, *chs))
    sem = BoundedSemaphore(len(channels))

    for c in channels:

        async def cont() -> None:
            async with sem:
                async for item in c:
                    try:
                        await out.send((c, item))
                    except ChanClosed:
                        break

        create_task(cont())

    async def close() -> None:
        pass

    create_task(close())
    return out


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
            async for _, item in await select(ch, *chs):
                try:
                    await out.send(item)
                except ChanClosed:
                    break

    create_task(cont())
    return out


# def fan_out(ch: Chan[T])
