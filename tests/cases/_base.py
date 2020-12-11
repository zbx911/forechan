from asyncio import TimeoutError, gather, wait_for
from itertools import repeat
from random import shuffle
from typing import Any, Awaitable, MutableSequence, Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Channel, ChannelClosed
from ..consts import REPEAT_FACTOR, SMOL_TIME, MODICUM_TIME
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

        async def test_3(self) -> None:
            await self.ch.send(1)

            async def c1() -> None:
                with self.assertRaises(ChannelClosed):
                    await self.ch.send(1)

            async def c2() -> None:
                with self.assertRaises(ChannelClosed):
                    await self.ch.send(1)

            await gather(c1(), c2(), self.ch.close())

        async def test_4(self) -> None:
            async def c1() -> None:
                with self.assertRaises(ChannelClosed):
                    await self.ch.recv()

            async def c2() -> None:
                with self.assertRaises(ChannelClosed):
                    await self.ch.recv()

            await gather(c1(), c2(), self.ch.close())

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
                await wait_for(self.ch.send(1), timeout=SMOL_TIME)

    class EmptyRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch.recv(), timeout=SMOL_TIME)

    class ManySendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.send(1)
            await gather(self.ch.send(1), self.ch.recv())
            await self.ch.recv()
            self.assertEqual(len(self.ch), 0)

        async def test_2(self) -> None:
            sends = repeat(self.ch.send(1), REPEAT_FACTOR)
            recvs = repeat(self.ch.recv(), REPEAT_FACTOR)
            cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
            shuffle(cos)
            await wait_for(gather(*cos), timeout=MODICUM_TIME)
            self.assertEqual(len(self.ch), 0)


BASE_CASES = tuple(extract_testcases(BaseCases))
