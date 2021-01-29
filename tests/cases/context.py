from asyncio import sleep
from math import inf
from unittest import IsolatedAsyncioTestCase

from ...forechan.context import ctx_with_parent, ctx_with_timeout


class ContextTimeout(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ttl = 20
        ctx = await ctx_with_timeout(ttl, val=None)
        self.assertAlmostEqual(ctx.ttl(), ttl, places=2)

    async def test_2(self) -> None:
        ttl = 20
        ctx = await ctx_with_timeout(ttl, val=None)
        await sleep(1)
        self.assertAlmostEqual(ctx.ttl(), ttl - 1, places=1)

    async def test_3(self) -> None:
        ttl = 0.5
        ctx = await ctx_with_timeout(ttl, val=None)
        await sleep(1)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)

    async def test_4(self) -> None:
        ttl = 0.5
        ctx = await ctx_with_timeout(ttl, val=None)
        await ([] << ctx.done)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)

    async def test_5(self) -> None:
        ttl = -10
        ctx = await ctx_with_timeout(ttl, val=None)
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)

    async def test_6(self) -> None:
        ttl = 10
        ctx = await ctx_with_timeout(ttl, val=None)
        ctx.cancel()
        self.assertEqual(ctx.ttl(), 0)
        self.assertFalse(ctx)


class ContextHeirarchy(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ttl = inf
        ctx1 = await ctx_with_timeout(ttl, val=None)
        ctx2 = ctx_with_parent(None, parent=ctx1)
        ctx3 = ctx_with_parent(None, parent=ctx2)

        ctx1.cancel()
        self.assertFalse(ctx1)
        self.assertFalse(ctx2)
        self.assertFalse(ctx3)

        self.assertAlmostEqual(ctx1.ttl(), ctx2.ttl())
        self.assertAlmostEqual(ctx2.ttl(), ctx3.ttl())

    async def test_2(self) -> None:
        ttl = 10
        ctx1 = await ctx_with_timeout(ttl, val=None)
        ctx2 = ctx_with_parent(None, parent=ctx1)
        ctx3 = ctx_with_parent(None, parent=ctx2)

        self.assertAlmostEqual(ctx1.ttl(), ctx2.ttl(), places=2)
        self.assertAlmostEqual(ctx2.ttl(), ctx3.ttl(), places=2)