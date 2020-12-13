from typing import Any, AsyncIterator, Tuple

from .types import Chan, ChanClosed


async def select(chan: Chan[Any], *chans: Chan[Any]) -> AsyncIterator[Tuple[Chan, Any]]:
    pass
