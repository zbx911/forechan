from inspect import getmembers, isclass
from itertools import product
from typing import Iterator, Protocol, Type
from unittest import IsolatedAsyncioTestCase

from ..forechan.types import Channel


def mixin_matrix(*classes: Iterator[Type]) -> Iterator[Type]:

    for bcs in product(*classes):

        class C(*bcs):
            __qualname__ = " |> ".join(bc.__qualname__ for bc in bcs)

        yield C


class HasChannel(Protocol):
    ch: Channel[int]


class BaseCases:
    class TestSendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            # await self.ch.send(1)
            # iden = await self.ch.recv()
            print(self.ch)
            self.assertEqual(1, 1)

    class TestDoubleSend(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            # await self.ch.send(1)
            # iden = await self.ch.recv()
            self.assertEqual(1, 1)


def every_basecase() -> Iterator[Type]:
    for _, member in getmembers(BaseCases):
        if isclass(member) and issubclass(member, IsolatedAsyncioTestCase):
            yield member
