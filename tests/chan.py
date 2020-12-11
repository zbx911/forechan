from unittest import IsolatedAsyncioTestCase

from ..forechan.chan import Chan
from ._base import BaseCases, Channel, HasChannel


class BaseSetup:
    class SetupChan(IsolatedAsyncioTestCase, HasChannel):
        def setUp(self) -> None:
            self.ch: Channel = Chan()


class TestSendRecv(BaseSetup.SetupChan, BaseCases.TestSendRecv):
    pass


class TestDoubleSend(BaseSetup.SetupChan, BaseCases.TestDoubleSend):
    pass
