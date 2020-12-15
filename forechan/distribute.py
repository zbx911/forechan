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
    ready: Deque[Chan[T]] = deque(maxlen=len(dest))

    for ch in dest:

        async def poll() -> None:
            while True:
                try:
                    await ch._on_sendable()
                except ChanClosed:
                    break
                else:
                    if ch not in ready:
                        ready.append(ch)

        create_task(poll())

    async def cont() -> None:
        async for item in src:
            sent = False
            while True:
                await ev.wait()
                while ready:
                    ch = ready.popleft()
                    try:
                        if ch.sendable():
                            ch.try_send(item)
                    except ChanClosed:
                        pass
                    else:
                        sent = True
                        break
                ev.clear()
                if sent:
                    break

    create_task(cont())