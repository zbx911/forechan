from asyncio import TimeoutError, gather, wait_for
from itertools import islice
from random import shuffle
from typing import Any, Awaitable, MutableSequence, Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Chan, ChanClosed
from ..consts import MODICUM_TIME, REPEAT_FACTOR, SMOL_TIME
from ..da import extract_testcases


class HasChannel(Protocol):
    ch: Chan[int]


class BaseCases:
    class Close(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            self.assertTrue(self.ch)

        async def test_2(self) -> None:
            await self.ch.close()
            self.assertFalse(self.ch)

        async def test_3(self) -> None:
            await (self.ch << 1)

            async def c1() -> None:
                with self.assertRaises(ChanClosed):
                    await (self.ch << 1)

            async def c2() -> None:
                with self.assertRaises(ChanClosed):
                    await (self.ch << 1)

            await gather(c1(), c2(), self.ch.close())

        async def test_4(self) -> None:
            async def c1() -> None:
                with self.assertRaises(ChanClosed):
                    await ([] << self.ch)

            async def c2() -> None:
                with self.assertRaises(ChanClosed):
                    await ([] << self.ch)

            await gather(c1(), c2(), self.ch.close())

    class SendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await (self.ch << 1)
            iden = await ([] << self.ch)
            self.assertEqual(iden, 1)

        async def test_2(self) -> None:
            await (self.ch << 1)
            iden = await ([] << self.ch)
            self.assertEqual(iden, 1)

    class SendToClosed(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChanClosed):
                await (self.ch << 1)

    class RecvFromClosed(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChanClosed):
                await ([] << self.ch)

    class DoubleSend(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await (self.ch << 1)
                await wait_for(self.ch << 1, timeout=SMOL_TIME)

    class EmptyRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for([] << self.ch, timeout=SMOL_TIME)

    class ManySendRecv(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await (self.ch << 1)
            await gather(self.ch << 1, [] << self.ch)
            await ([] << self.ch)
            self.assertEqual(len(self.ch), 0)

        async def test_2(self) -> None:
            sends = islice(iter(lambda: self.ch << 1, None), REPEAT_FACTOR)
            recvs = islice(iter(lambda: () << self.ch, None), REPEAT_FACTOR)
            cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
            shuffle(cos)
            await wait_for(gather(*cos), timeout=MODICUM_TIME)
            self.assertEqual(len(self.ch), 0)

    class ClosedNotif(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._closed_notif(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await self.ch.close()
            await wait_for(self.ch._closed_notif(), timeout=SMOL_TIME)

        async def test_3(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChanClosed):
                await wait_for(self.ch._sendable_notif(), timeout=SMOL_TIME)
            with self.assertRaises(ChanClosed):
                await wait_for(self.ch._recvable_notif(), timeout=SMOL_TIME)

    class SendableNotif(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            await (self.ch << 1)
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._sendable_notif(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await wait_for(self.ch._sendable_notif(), timeout=SMOL_TIME)

    class RecvableNotif(IsolatedAsyncioTestCase, HasChannel):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._recvable_notif(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await (self.ch << 1)
            await wait_for(self.ch._recvable_notif(), timeout=SMOL_TIME)


BASE_CASES = tuple(extract_testcases(BaseCases))
