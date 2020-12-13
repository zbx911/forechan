from asyncio.tasks import create_task
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from .chan import chan
from .types import Chan, ChanClosed
from .wait_group import wait_group

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


@overload
async def select(
    ch1: Chan[T], ch2: Chan[U]
) -> Chan[Tuple[Union[Chan[T], Chan[U]], Union[T, U]]]:
    ...


@overload
async def select(
    ch1: Chan[T], ch2: Chan[U], ch3: Chan[V]
) -> Chan[Tuple[Union[Chan[T], Chan[U], Chan[V]], Union[T, U, V]]]:
    ...


async def select(ch: Chan[Any], *chs: Chan[Any]) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    wg = wait_group()
    channels: Sequence[Chan[Any]] = tuple((ch, *chs))

    for c in channels:

        async def cont() -> None:
            with wg:
                async for item in c:
                    try:
                        await out.send((c, item))
                    except ChanClosed:
                        break

        create_task(cont())

    async def close() -> None:
        await wg.wait()
        out.close()

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
