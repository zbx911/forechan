from unittest import IsolatedAsyncioTestCase


from ..forechan.chan import Chan
from ._base import BASE_CASES, Channel, HasChannel
from ._da import mixin_matrix, mk_loader


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


class Moo(IsolatedAsyncioTestCase):
    async def test(self) -> None:
        self.assertEqual(5, 5)


load_tests = mk_loader(*mixin_matrix((BaseSetup.SetupChan,), BASE_CASES))