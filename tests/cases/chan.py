from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ...forechan.types import Chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChannel


class ChanBaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        async def asyncSetUp(self) -> None:
            self.ch = chan(int)


TEST_MATRIX = polyclass_matrix(extract_testcases(ChanBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
