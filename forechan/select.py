from asyncio.locks import Event
from asyncio.tasks import create_task
from itertools import chain
from typing import Any, Set, Tuple

from ._ops import cascading_close
from .chan import chan
from .types import Chan, ChanClosed
from .wait_group import wait_group


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    wg = wait_group()
    ready: Set[Chan[Any]] = set()
    ev = Event()

    if cascade_close:
        await cascading_close((out,), dest=(ch, *chs))
    await cascading_close((ch, *chs), dest=(out,))

    for c in chain((ch,), chs):

        async def clo() -> None:
            with wg:
                await c._closed_notif()

        create_task(clo())

        async def notif() -> None:
            while True:
                try:
                    await c._recvable_notif()
                except ChanClosed:
                    break

        create_task(notif())

    async def cont() -> None:
        while out:
            await ev.wait()
            while ready:
                c = ready.pop()
                if len(c):
                    item = await c.recv()
                    ev.clear()
                    try:
                        await out.send((c, item))
                    except ChanClosed:
                        pass
                    break

    create_task(cont())
    return out
