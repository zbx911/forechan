from asyncio.locks import Event
from asyncio.tasks import create_task
from collections import deque
from itertools import chain
from typing import Any, Deque, Set, Tuple

from .chan import chan
from .ops import cascading_close
from .types import Chan, ChanClosed


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    ev = Event()
    ready: Deque[Chan[Any]] = deque()
    ready_set: Set[Chan[Any]] = set()

    if cascade_close:
        await cascading_close((out,), dest=(ch, *chs))
    await cascading_close((ch, *chs), dest=(out,))

    for c in chain((ch,), chs):

        async def poll() -> None:
            while True:
                try:
                    await c._on_recvable()
                except ChanClosed:
                    break
                else:
                    if c not in ready_set:
                        ready_set.add(c)
                        ready.append(c)

        create_task(poll())

    async def cont() -> None:
        while out:
            await ev.wait()
            while ready:
                c = ready.pop()
                ready_set.remove(c)
                if c._recvable():
                    item = c.try_recv()
                    try:
                        await out.send((c, item))
                    except ChanClosed:
                        pass
                    else:
                        ev.clear()
                        break

    create_task(cont())
    return out
