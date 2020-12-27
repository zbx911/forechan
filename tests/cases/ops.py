from asyncio.tasks import create_task
from typing import AsyncIterator
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.ops import to_chan
from ..consts import BIG_REP_FACTOR


async def count_to_rep() -> AsyncIterator[int]:
    for i in range(BIG_REP_FACTOR):
        yield i


class ToChan(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ch = chan(int)
        create_task(to_chan(count_to_rep(), ch))
        i = -1
        async for i in ch:
            pass
        self.assertEqual(i, BIG_REP_FACTOR - 1)
        self.assertFalse(ch)

    async def test_2(self) -> None:
        ch = chan(int)
        create_task(to_chan(count_to_rep(), ch))
        i = -1
        async for i in ch:
            pass

        self.assertEqual(i, BIG_REP_FACTOR - 1)
        self.assertFalse(ch)
