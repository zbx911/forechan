from __future__ import annotations

from abc import abstractmethod
from asyncio.tasks import create_task, sleep
from math import isinf
from time import monotonic
from typing import MutableSequence, Optional, Protocol

from .broadcast import broadcast
from .types import Boolable, Chan


class Context(Boolable, Protocol):
    @property
    @abstractmethod
    def done(self) -> Chan[None]:
        """
        a `broadcast` chan of cancellation signifier
        """

    @abstractmethod
    def ttl(self) -> float:
        """
        how many seconds until scheduled cancellation
        can be `inf`
        """

    @abstractmethod
    def cancel(self) -> None:
        """
        turn on `cancelled` chan
        """

    @abstractmethod
    def attach(self, child: Context) -> None:
        """
        children are cancelled when parents are
        """


class _Context(Context):
    def __init__(self, deadline: float) -> None:
        self._ch: Chan[None] = broadcast(None)
        self._deadline = deadline
        self._children: MutableSequence[Context] = []

    def __bool__(self) -> bool:
        return not self.done.recvable()

    @property
    def done(self) -> Chan[None]:
        return self._ch

    def ttl(self) -> float:
        return max(self._deadline - monotonic(), 0.0) if self else 0.0

    def cancel(self) -> None:
        for child in self._children:
            child.cancel()
        self.done.try_send(None)

    def attach(self, child: Context) -> None:
        self._children.append(child)
        if not self:
            child.cancel()


async def ctx_with_timeout(ttl: float, parent: Optional[Context] = None) -> Context:
    monotonic_deadline = monotonic() + ttl
    ctx = _Context(deadline=monotonic_deadline)
    if parent is not None:
        parent.attach(ctx)

    if not isinf(ttl):

        async def cont() -> None:
            await sleep(ttl)
            ctx.cancel()

        create_task(cont())

    return ctx
