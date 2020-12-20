from itertools import count
from typing import Awaitable, Callable, Optional, Tuple, Type, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")


async def mb_from(
    ask: Chan[Tuple[int, T]], reply: Chan[Tuple[int, U]]
) -> Callable[[T], Awaitable[U]]:
    it = count()

    async def req(qst: T) -> U:
        uid = next(it)
        await ask.send((uid, qst))
        while reply:
            await reply._on_recvable()
            if reply.recvable():
                rid, _ = reply.try_peek()
                if rid == uid:
                    _, item = reply.try_recv()
                    return item
        else:
            raise ChanClosed()

    return req


async def mb(
    t: Optional[Type[T]] = None, u: Optional[Type[U]] = None
) -> Tuple[Chan[Tuple[int, T]], Chan[Tuple[int, U]], Callable[[T], Awaitable[U]]]:
    ask: Chan[Tuple[int, T]] = chan()
    reply: Chan[Tuple[int, U]] = chan()
    req = await mb_from(ask, reply=reply)
    return ask, reply, req
