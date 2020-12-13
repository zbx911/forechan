from asyncio.tasks import gather
from itertools import chain
from typing import Any

from .types import Chan


async def close(ch: Chan[Any], *chs: Chan[Any], close: bool) -> None:
    if close:
        await gather(*(c.close() for c in chain((ch,), chs)))
