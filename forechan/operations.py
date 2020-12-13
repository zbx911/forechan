from asyncio.tasks import create_task, gather
from itertools import chain, islice
from typing import (
    Any,
    AsyncIterator,
    Callable,
    MutableSequence,
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
W = TypeVar("W")


async def _close(ch: Chan[Any], *chs: Chan[Any], close: bool) -> None:
    if close:
        await gather(*(c.close() for c in chain((ch,), chs)))


# @overload
# async def select(
#     ch1: Chan[T], ch2: Chan[U], cascade_close: bool = True
# ) -> Chan[Union[Tuple[Chan[T], T], Tuple[Chan[U], U]]]:
#     ...


# @overload
# async def select(
#     ch1: Chan[T], ch2: Chan[U], ch3: Chan[V], cascade_close: bool = True
# ) -> Chan[Union[Tuple[Chan[T], T], Tuple[Chan[U], U], Tuple[Chan[V], V]]]:
#     ...


# @overload
# async def select(
#     ch1: Chan[T], ch2: Chan[U], ch3: Chan[V], ch4: Chan[W], cascade_close: bool = True
# ) -> Chan[
#     Union[Tuple[Chan[T], T], Tuple[Chan[U], U], Tuple[Chan[V], V], Tuple[Chan[W], W]]
# ]:
#     ...


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    channels: Sequence[Chan[Any]] = tuple((ch, *chs))
    out: Chan[Any] = chan()
    wg = wait_group()

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
    cascade_close: bool = True,
) -> Chan[U]:
    out: Chan[U] = chan()

    async def cont() -> None:
        async with out:
            async for item in trans(ch):
                try:
                    await out.send(item)
                except ChanClosed:
                    await _close(ch, close=cascade_close)

    create_task(cont())
    return out


async def fan_in(ch: Chan[T], *chs: Chan[T], cascade_close: bool = True) -> Chan[T]:
    channels: Sequence[Chan[Any]] = tuple((ch, *chs))
    out: Chan[T] = chan()

    async def cont() -> None:
        async with out:
            async for _, item in await select(*channels):
                try:
                    await out.send(item)
                except ChanClosed:
                    await _close(ch, *chs, close=cascade_close)

    create_task(cont())
    return out


async def fan_out(ch: Chan[T], n: int, cascade_close: bool = True) -> Sequence[Chan[T]]:
    if n < 2:
        raise ValueError()

    channels: MutableSequence[Chan[T]] = [*islice(iter(chan, None), n)]

    async def cont() -> None:
        async for item in ch:
            channels[:] = [out for out in channels if out]
            if not channels:
                await _close(ch, close=cascade_close)
                break

    create_task(cont())
    return channels
