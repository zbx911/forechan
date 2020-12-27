from unittest import IsolatedAsyncioTestCase

from ...forechan.bufs import NormalBuf, SlidingBuf, DroppingBuf


class BufSetup:
    class SetupNormal(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = NormalBuf[int](maxlen=1)

    class SetupSliding(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = SlidingBuf[int](maxlen=1)

    class SetupDropping(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = DroppingBuf[int](maxlen=1)
