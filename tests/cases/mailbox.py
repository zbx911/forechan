from itertools import count
from typing import Tuple
from unittest import IsolatedAsyncioTestCase

from ...forechan.go import go
from ...forechan.mailbox import mb
from ...forechan.types import Chan
from ..consts import BIG_REP_FACTOR


async def echo(
    ask: Chan[Tuple[int, int]], reply: Chan[Tuple[int, int]], cycles: int
) -> None:
    assert cycles >= 1
    it = count(1)
    async for qid, n in ask:
        await (reply << (qid, n))
        i = next(it)
        if i == cycles:
            break


class MailBoxSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.ask, self.reply, self.req = await mb(int, int)


class MailBoxAskReply(MailBoxSetup.SetupChan):
    async def test_1(self) -> None:
        await go(echo(self.ask, reply=self.reply, cycles=BIG_REP_FACTOR))
        with self.subTest():
            for i in range(BIG_REP_FACTOR):
                ans = await self.req(i)
                self.assertEqual(ans, i)