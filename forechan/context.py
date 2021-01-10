from __future__ import annotations

from abc import abstractmethod
from asyncio.tasks import create_task, sleep
from datetime import datetime, timedelta, timezone
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
        how many seconds left until scheduled cancellation
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
        seconds = max(self._deadline - monotonic(), 0.0) if self else 0.0
        return seconds

    def cancel(self) -> None:
        for child in self._children:
            child.cancel()
        self.done.try_send(None)

    def attach(self, child: Context) -> None:
        self._children.append(child)
        if not self:
            child.cancel()


async def ctx_with_timeout(ttl: timedelta, parent: Optional[Context] = None) -> Context:
    ttl_seconds = ttl.total_seconds()
    monotonic_deadline = monotonic() + ttl_seconds
    ctx = _Context(deadline=monotonic_deadline)
    if parent is not None:
        parent.attach(ctx)

    if ttl_seconds <= 0:
        ctx.cancel()

    else:

        async def cont() -> None:
            await sleep(ttl_seconds)
            ctx.cancel()

        create_task(cont())

    return ctx


async def ctx_with_deadline(
    deadline: datetime, parent: Optional[Context] = None
) -> Context:
    ttl = deadline - datetime.now(tz=timezone.utc)
    return await ctx_with_timeout(ttl, parent=parent)
