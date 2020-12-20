from itertools import count
from typing import Awaitable, Callable, Iterator, Optional, Tuple, Type, TypeVar

from .chan import chan
from .types import Chan, ChanClosed

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")


async def mb_from(
    ask: Chan[Tuple[K, T]], reply: Chan[Tuple[K, U]], uids: Iterator[K]
) -> Callable[[T], Awaitable[U]]:
    """
    useful in calls across a network

    `<async T -> U>` facade over two chans of out of order messages

    `| ->  req<T> -> |`  in independent loop
    `| <- resp<U> <- |`  in independent loop

    each req,resp pair is marked with unique id `K`
    """

    async def req(qst: T) -> U:
        uid = next(uids)
        await ask.send((uid, qst))
        while reply:
            await reply._on_recvable()
            if reply.recvable():
                rid, _ = reply.try_peek()
                if rid == uid:
                    _, resp = reply.try_recv()
                    return resp
        else:
            raise ChanClosed()

    return req


async def mb(
    t: Optional[Type[T]] = None, u: Optional[Type[U]] = None
) -> Tuple[Chan[Tuple[int, T]], Chan[Tuple[int, U]], Callable[[T], Awaitable[U]]]:
    """
    see `mb_from`
    """

    uids = count()
    ask: Chan[Tuple[int, T]] = chan()
    reply: Chan[Tuple[int, U]] = chan()
    req = await mb_from(ask, reply=reply, uids=uids)
    return ask, reply, req
