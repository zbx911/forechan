from asyncio import sleep
from math import inf
from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.context import ctx_with_timeout
from ...forechan.go import go


class ContextTimeout(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ctx = await ctx_with_timeout(inf)
        self.assertEqual(ctx.ttl(), inf)

    async def test_2(self) -> None:
        ttl = 20
        ctx = await ctx_with_timeout(ttl)
        self.assertAlmostEqual(ctx.ttl(), ttl, places=2)

    async def test_3(self) -> None:
        ttl = 20
        ctx = await ctx_with_timeout(ttl)
        await sleep(1)
        self.assertAlmostEqual(ctx.ttl(), ttl - 1, places=1)

    async def test_4(self) -> None:
        ttl = 0.5
        ctx = await ctx_with_timeout(ttl)
        await sleep(1)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)

    async def test_5(self) -> None:
        ttl = 0.5
        ctx = await ctx_with_timeout(ttl)
        await ([] << ctx.done)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)

    async def test_6(self) -> None:
        ttl = -10
        ctx = await ctx_with_timeout(ttl)
        await sleep(0)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)