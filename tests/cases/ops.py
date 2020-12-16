from typing import AsyncIterator
from unittest import IsolatedAsyncioTestCase

from ..consts import REPEAT_FACTOR

from ...forechan.ops import to_chan
from ..da import profiler


async def count_to_rep() -> AsyncIterator[int]:
    for i in range(REPEAT_FACTOR):
        yield i


class ToChan(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ch = await to_chan(count_to_rep())
        with profiler():
            async for _ in ch:
                pass

        self.assertFalse(ch)

    async def test_2(self) -> None:
        ch = await to_chan(range(REPEAT_FACTOR))
        with profiler():
            async for _ in ch:
                pass

        self.assertFalse(ch)