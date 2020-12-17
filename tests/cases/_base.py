from asyncio import TimeoutError, create_task, gather, wait_for
from itertools import islice
from random import shuffle
from typing import Any, Awaitable, MutableSequence, Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Chan, ChanClosed, ChanEmpty, ChanFull
from ..consts import MODICUM_TIME, REPEAT_FACTOR, SMOL_TIME
from ..da import extract_testcases


class HasChan(Protocol):
    ch: Chan[int]


class BaseCases:
    class TypeConformance(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            self.assertIsInstance(self.ch, Chan)

    class Close(IsolatedAsyncioTestCase, HasChan):
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

            await self.ch.close()
            await gather(c1(), c2())

        async def test_4(self) -> None:
            async def c1() -> None:
                with self.assertRaises(ChanClosed):
                    await ([] << self.ch)

            async def c2() -> None:
                with self.assertRaises(ChanClosed):
                    await ([] << self.ch)

            await self.ch.close()
            await gather(c1(), c2())

    class SendRecvSync(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            (self.ch < 1)
            iden = [] < self.ch
            self.assertEqual(iden, 1)

        async def test_2(self) -> None:
            (self.ch < 1)
            with self.assertRaises(ChanFull):
                (self.ch < 1)

        async def test_3(self) -> None:
            with self.assertRaises(ChanEmpty):
                ([] < self.ch)

    class SendRecv(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            await (self.ch << 1)
            iden = await ([] << self.ch)
            self.assertEqual(iden, 1)

    class SendToClosed(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChanClosed):
                await (self.ch << 1)

    class RecvFromClosed(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            await self.ch.close()
            with self.assertRaises(ChanClosed):
                await ([] << self.ch)

    class DoubleSend(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await (self.ch << 1)
                await wait_for(self.ch << 1, timeout=SMOL_TIME)

    class EmptyRecv(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for([] << self.ch, timeout=SMOL_TIME)

    class ManySendRecv(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            await (self.ch << 1)
            await gather(self.ch << 1, [] << self.ch)
            await ([] << self.ch)
            self.assertEqual(len(self.ch), 0)

        async def test_2(self) -> None:
            async def cont() -> None:
                await gather([] << self.ch, [] << self.ch)

            task = create_task(cont())
            await wait_for(gather(task, self.ch << 1, self.ch << 1), timeout=SMOL_TIME)

        async def test_3(self) -> None:
            nums = 10

            async def c1() -> None:
                async with self.ch:
                    for i in range(nums + 1):
                        await (self.ch << i)

            async def c2() -> None:
                i = -1
                async for i in self.ch:
                    pass
                self.assertEqual(i, nums)

            await wait_for(gather(c1(), c2()), timeout=MODICUM_TIME)

        async def test_4(self) -> None:
            sends = islice(iter(lambda: self.ch << 1, None), REPEAT_FACTOR)
            recvs = islice(iter(lambda: () << self.ch, None), REPEAT_FACTOR)
            cos: MutableSequence[Awaitable[Any]] = [*sends, *recvs]
            shuffle(cos)
            await wait_for(gather(*cos), timeout=MODICUM_TIME)
            self.assertEqual(len(self.ch), 0)

    class ClosedNotif(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._on_closed(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await self.ch.close()
            await wait_for(self.ch._on_closed(), timeout=SMOL_TIME)

        async def test_3(self) -> None:
            await self.ch.close()
            ch1 = await wait_for(self.ch._on_sendable(), timeout=SMOL_TIME)
            ch2 = await wait_for(self.ch._on_recvable(), timeout=SMOL_TIME)
            self.assertFalse(ch1)
            self.assertFalse(ch2)

    class SendableNotif(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            await (self.ch << 1)
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._on_sendable(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await wait_for(self.ch._on_sendable(), timeout=SMOL_TIME)

    class RecvableNotif(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            with self.assertRaises(TimeoutError):
                await wait_for(self.ch._on_recvable(), timeout=SMOL_TIME)

        async def test_2(self) -> None:
            await (self.ch << 1)
            await wait_for(self.ch._on_recvable(), timeout=SMOL_TIME)

    class PerformanceProfilng(IsolatedAsyncioTestCase, HasChan):
        async def test_1(self) -> None:
            pass


BASE_CASES = tuple(extract_testcases(BaseCases))
