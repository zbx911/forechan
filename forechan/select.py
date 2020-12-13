from asyncio.locks import Event
from asyncio.tasks import create_task
from itertools import chain
from typing import Any, Set, Tuple, TypeVar, Union, overload

from .chan import chan
from .operations import close
from .types import Chan
from .wait_group import wait_group

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


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
    out: Chan[Any] = chan()
    wg = wait_group()
    channels: Set[Chan[Any]] = set()
    ev = Event()

    async def close_upstream() -> None:
        await out._closed_notif()
        await close(ch, *chs, close=cascade_close)

    create_task(close_upstream())

    for c in chain((ch,), chs):

        async def clo() -> None:
            with wg:
                await c._closed_notif()

        create_task(clo())

        async def notif() -> None:
            while c:
                await c._recvable_notif()

        create_task(notif())

    async def fin() -> None:
        await wg.wait()
        out.close()

    create_task(fin())

    async def cont() -> None:
        while out:
            await ev.wait()
            while channels:
                c = channels.pop()
                if len(c):
                    item = await c.recv()
                    ev.clear()
                    await out.send((c, item))
                    break

    create_task(cont())
    return out
