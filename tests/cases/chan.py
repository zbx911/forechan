from unittest import IsolatedAsyncioTestCase

from ...forechan.chan import Chan
from ..da import extract_testcases, mk_loader, polyclass_matrix
from ._base import BASE_CASES, Channel, HasChannel


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


class Moo(IsolatedAsyncioTestCase):
    async def test(self) -> None:
        print("moo")
        self.assertEqual(5, 5)


load_tests = mk_loader(*polyclass_matrix(extract_testcases(BaseSetup), BASE_CASES))
