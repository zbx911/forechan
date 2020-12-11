from asyncio import TimeoutError, wait_for
from typing import Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Channel, ChannelClosed
from ..da import extract_testcases


class HasChannel(Protocol):
    ch: Channel[int]


class BaseCases:
    class SendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.send(1)
            iden = await self.ch.recv()
            self.assertEqual(iden, 1)

        async def test_2(self) -> None:
            await self.ch.send(1)
            iden = await self.ch.recv()
            self.assertEqual(iden, 1)

    class SendToClosed(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChannelClosed):
                await self.ch.send(1)

    class RecvFromClosed(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChannelClosed):
                await self.ch.recv()

    class DoubleSend(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await self.ch.send(1)
                await wait_for(self.ch.send(1), timeout=0.01)

    class EmptyRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch.recv(), timeout=0.01)


BASE_CASES = tuple(extract_testcases(BaseCases))
