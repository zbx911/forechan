from asyncio.locks import Event
from asyncio.tasks import create_task, gather
from collections import deque
from typing import Deque, TypeVar

from .ops import cascading_close
from .types import Chan, ChanClosed

T = TypeVar("T")


async def distribute(src: Chan[T], *dest: Chan[T], cascade_close: bool = True) -> None:
    if not dest:
        raise ValueError()

    if cascade_close:
        await gather(
            cascading_close((src,), dest=dest), cascading_close(dest, dest=(src,))
        )

    ev = Event()
    ready: Deque[Chan[T]] = deque()

    for ch in dest:

        async def poll() -> None:
            while True:
                try:
                    await ch._on_sendable()
                except ChanClosed:
                    break
                else:
                    ev.set()
                    ready.append(ch)

        create_task(poll())

    async def cont() -> None:
        while True:
            if not ready:
                await ev.wait()
                ev.clear()
            try:
                await src._on_recvable()
            except ChanClosed:
                return
            else:
                while ready:
                    c = ready.popleft()
                    if c._recvable():
                        item = src.try_recv()
                        c.try_send(item)
                        break

    create_task(cont())