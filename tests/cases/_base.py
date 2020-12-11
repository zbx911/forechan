from typing import Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Channel, ChannelClosed
from ..da import extract_testcases


class HasChannel(Protocol):
    ch: Channel[int]


class BaseCases:
    class SendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            await self.ch.send(1)
            iden = await self.ch.recv()
            self.assertEqual(iden, 1)

    class Send2Closed(IsolatedAsyncioTestCase, HasChannel):
        async def test(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChannelClosed):
                await self.ch.send(1)


BASE_CASES = tuple(extract_testcases(BaseCases))
