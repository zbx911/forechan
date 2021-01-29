from __future__ import annotations

from abc import abstractmethod
from asyncio.tasks import create_task, sleep
from datetime import datetime, timezone
from math import isfinite
from time import monotonic
from typing import MutableSequence, Optional, Protocol, TypeVar

from .broadcast import broadcast
from .types import Boolable, Chan

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Context(Boolable, Protocol[T_co]):
    @property
    @abstractmethod
    def val(self) -> T_co:
        """
        Context can carry an immutable value
        """

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


class _Context(Context[T_co]):
    def __init__(self, val: T_co, deadline: float) -> None:
        self._v = val
        self._ch: Chan[None] = broadcast(None)
        self._deadline = deadline
        self._children: MutableSequence[Context] = []

    def __bool__(self) -> bool:
        return not self.done.recvable()

    @property
    def val(self) -> T_co:
        return self._v

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


async def ctx_with_timeout(
    ttl_seconds: float, val: T, parent: Optional[Context] = None
) -> Context[T]:
    monotonic_deadline = monotonic() + ttl_seconds
    ctx = _Context(val=val, deadline=monotonic_deadline)
    if parent is not None:
        parent.attach(ctx)

    if ttl_seconds <= 0:
        ctx.cancel()

    elif isfinite(ttl_seconds):

        async def cont() -> None:
            await sleep(ttl_seconds)
            ctx.cancel()

        create_task(cont())

    return ctx


async def ctx_with_deadline(
    deadline: datetime, val: T, parent: Optional[Context] = None
) -> Context[T]:
    ttl = (deadline - datetime.now(tz=timezone.utc)).total_seconds()
    return await ctx_with_timeout(ttl, val=val, parent=parent)
