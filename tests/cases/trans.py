from typing import AsyncIterator
from unittest.case import TestCase

from ...forechan.chan import mk_chan
from ...forechan.trans import trans
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChannel


async def xform(it: AsyncIterator[int]) -> AsyncIterator[int]:
    async for n in it:
        yield n + 1


class TransBaseSetup:
    class SetupChan(TestCase, HasChannel):
        def setUp(self) -> None:
            self.p = mk_chan(int)
            self.ch = trans(xform, chan=self.p)


TEST_MATRIX = polyclass_matrix(extract_testcases(TransBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
