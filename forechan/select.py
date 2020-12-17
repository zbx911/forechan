from asyncio.locks import Event
from asyncio.tasks import create_task
from collections import deque
from itertools import chain
from typing import Any, Deque, Tuple

from .chan import chan
from .ops import cascading_close
from .types import Chan, ChanClosed


async def select(
    ch: Chan[Any], *chs: Chan[Any], cascade_close: bool = True
) -> Chan[Tuple[Chan[Any], Any]]:
    out: Chan[Any] = chan()
    ev = Event()
    ready: Deque[Chan[Any]] = deque()

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
                    ev.set()
                    ready.append(c)

        create_task(poll())

    async def cont() -> None:
        while True:
            if not ready:
                await ev.wait()
                ev.clear()
            try:
                await out._on_sendable()
            except ChanClosed:
                return
            else:
                while ready:
                    c = ready.popleft()
                    if c._recvable():
                        item = c.try_recv()
                        out.try_send((c, item))
                        break

    create_task(cont())
    return out
