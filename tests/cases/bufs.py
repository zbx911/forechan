from unittest import IsolatedAsyncioTestCase

from ...forechan.bufs import NormalBuf, SlidingBuf, DroppingBuf
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._buf_base import BASE_CASES, HasBuf


class BufBaseSetup:
    class SetupNormal(IsolatedAsyncioTestCase, HasBuf):
        async def asyncSetUp(self) -> None:
            self.buf = NormalBuf[int](maxlen=1)

    class SetupSliding(IsolatedAsyncioTestCase, HasBuf):
        async def asyncSetUp(self) -> None:
            self.buf = SlidingBuf[int](maxlen=1)

    class SetupDropping(IsolatedAsyncioTestCase, HasBuf):
        async def asyncSetUp(self) -> None:
            self.buf = DroppingBuf[int](maxlen=1)


TEST_MATRIX = polyclass_matrix(extract_testcases(BufBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
