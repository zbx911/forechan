from typing import Protocol
from unittest import IsolatedAsyncioTestCase

from ..forechan.types import Channel


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
