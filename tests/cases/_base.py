from asyncio import TimeoutError, gather, wait_for
from itertools import repeat
from random import shuffle
from typing import Any, Awaitable, MutableSequence, Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Channel, ChannelClosed
from ..da import extract_testcases


class HasChannel(Protocol):
    ch: Channel[int]


class BaseCases:
    class Close(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            self.assertTrue(self.ch)

        async def test_2(self) -> None:
            await self.ch.close()
            self.assertFalse(self.ch)

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

    class ManySendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.send(1)
            await gather(self.ch.send(1), self.ch.recv())
            await self.ch.recv()
            self.assertEqual(len(self.ch), 0)

        async def test_2(self) -> None:
            reps = 100
            sends = repeat(self.ch.send(1), reps)
            recvs = repeat(self.ch.recv(), reps)
            cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
            shuffle(cos)
            await wait_for(gather(*cos), timeout=0.1)
            self.assertEqual(len(self.ch), 0)


BASE_CASES = tuple(extract_testcases(BaseCases))
