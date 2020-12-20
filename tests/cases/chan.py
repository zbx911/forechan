from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChan


class ChanSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChan[int]):
        async def asyncSetUp(self) -> None:
            self.ch = chan(int)


TEST_MATRIX = polyclass_matrix(extract_testcases(ChanSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
