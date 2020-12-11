from unittest import IsolatedAsyncioTestCase

from ..forechan.chan import Chan
from ._base import BASE_CASES, Channel, HasChannel
from ._da import mk_loader, polyclass_matrix


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


class Moo(IsolatedAsyncioTestCase):
    async def test(self) -> None:
        self.assertEqual(5, 5)


load_tests = mk_loader(*polyclass_matrix((BaseSetup.SetupChan,), BASE_CASES))
