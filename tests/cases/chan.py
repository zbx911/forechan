from unittest.case import TestCase

from ...forechan.chan import mk_chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, HasChannel


class ChanBaseSetup:
    class SetupChan(TestCase, HasChannel):
        def setUp(self) -> None:
            self.ch = mk_chan(int)


TEST_MATRIX = polyclass_matrix(extract_testcases(ChanBaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
