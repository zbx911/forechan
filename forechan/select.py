from asyncio.tasks import create_task
from typing import Any, AsyncIterator, MutableSequence, Tuple

from ._da import race
from .types import Chan


async def select(*cs: Chan[Any]) -> AsyncIterator[Tuple[Chan[Any], Any]]:
    """
    async for ch, item in select(ch1, ch2, ch3, ...):
    if ch == ch1:
        ...
    elif ch == ch2:
        ...
    elif ch == ch3:
        ...
    """

    chans: MutableSequence[Chan[Any]] = [*cs]

    while chans:
        _ready, _, _ = await race(*(create_task(c._on_recvable()) for c in chans))
        ready = _ready.result()

        if not ready:
            chans[:] = [c for c in chans if c]
        elif ready.recvable():
            yield ready, ready.try_recv()
