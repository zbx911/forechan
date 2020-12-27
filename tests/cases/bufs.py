from unittest import IsolatedAsyncioTestCase

from ...forechan.bufs import NormalBuf, SlidingBuf, DroppingBuf


class Setup:
    class Normal(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = NormalBuf[int](maxlen=1)

    class Sliding(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = SlidingBuf[int](maxlen=1)

    class Dropping(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.buf = DroppingBuf[int](maxlen=1)
