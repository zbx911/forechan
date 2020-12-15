from asyncio.locks import Event
from asyncio.tasks import create_task
from collections import deque
from itertools import chain
from typing import Any, Deque, Tuple

from .ops import cascading_close
from .chan import chan
from .types import Chan, ChanClosed


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    ev = Event()
    ready: Deque[Chan[Any]] = deque(maxlen=len(chs) + 1)

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
                    if c not in ready:
                        ready.append(c)

        create_task(poll())

    async def cont() -> None:
        while out:
            await ev.wait()
            while ready:
                c = ready.pop()
                try:
                    if not c.empty():
                        item = c.try_recv()
                        await out.send((c, item))
                except ChanClosed:
                    pass
                else:
                    ev.clear()
                    break

    create_task(cont())
    return out
