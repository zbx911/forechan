from unittest.case import TestCase

from ...forechan.chan import Chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, Channel, HasChannel


class BaseSetup:
    class SetupChan(TestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


TEST_MATRIX = polyclass_matrix(extract_testcases(BaseSetup), BASE_CASES)
load_tests = mk_loader(*TEST_MATRIX)
