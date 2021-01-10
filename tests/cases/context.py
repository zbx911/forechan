from asyncio import sleep
from unittest import IsolatedAsyncioTestCase
from datetime import timedelta
from ...forechan.context import ctx_with_timeout


class ContextTimeout(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ttl = timedelta(seconds=20)
        ctx = await ctx_with_timeout(ttl)
        self.assertAlmostEqual(ctx.ttl().total_seconds(), ttl.total_seconds(), places=2)

    async def test_2(self) -> None:
        ttl = timedelta(seconds=20)
        ctx = await ctx_with_timeout(ttl)
        await sleep(1)
        self.assertAlmostEqual(
            ctx.ttl().total_seconds(), ttl.total_seconds() - 1, places=1
        )

    async def test_3(self) -> None:
        ttl = timedelta(seconds=0.5)
        ctx = await ctx_with_timeout(ttl)
        await sleep(1)
        self.assertEqual(ctx.ttl().total_seconds(), 0)
        self.assertFalse(ctx)

    async def test_4(self) -> None:
        ttl = timedelta(seconds=0.5)
        ctx = await ctx_with_timeout(ttl)
        await ([] << ctx.done)
        self.assertEqual(ctx.ttl().total_seconds(), 0)
        self.assertFalse(ctx)

    async def test_5(self) -> None:
        ttl = -timedelta(seconds=10)
        ctx = await ctx_with_timeout(ttl)
        self.assertEqual(ctx.ttl().total_seconds(), 0)
        self.assertFalse(ctx)

    async def test_6(self) -> None:
        ttl = timedelta(seconds=10)
        ctx = await ctx_with_timeout(ttl)
        ctx.cancel()
        self.assertEqual(ctx.ttl().total_seconds(), 0)
        self.assertFalse(ctx)


class ContextHeirarchy(IsolatedAsyncioTestCase):
    async def test_1(self) -> None:
        ttl = timedelta.max
        ctx1 = await ctx_with_timeout(ttl)
        ctx2 = await ctx_with_timeout(ttl, parent=ctx1)
        ctx3 = await ctx_with_timeout(ttl, parent=ctx2)

        ctx1.cancel()
        self.assertFalse(ctx1)
        self.assertFalse(ctx2)
        self.assertFalse(ctx3)
