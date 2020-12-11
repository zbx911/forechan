from inspect import getmembers, isclass
from typing import Iterator, Protocol, Type
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Channel


class HasChannel(Protocol):
    ch: Channel[int]


class BaseCases:
    class TestSendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            # await self.ch.send(1)
            # iden = await self.ch.recv()
            print(type(self).__qualname__)
            self.assertEqual(1, 1)

    class TestDoubleSend(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            # await self.ch.send(1)
            # iden = await self.ch.recv()
            print(type(self).__qualname__)
            self.assertEqual(1, 1)


def _every_basecase() -> Iterator[Type]:
    for _, member in getmembers(BaseCases):
        if isclass(member) and issubclass(member, IsolatedAsyncioTestCase):
            yield member


BASE_CASES = tuple(_every_basecase())
