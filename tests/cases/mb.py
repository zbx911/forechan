from asyncio.tasks import create_task
from itertools import count
from typing import Tuple
from unittest import IsolatedAsyncioTestCase

from ...forechan.mb import mb
from ...forechan.types import Chan


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


class MailBoxBaseSetup:
    class SetupChan(IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.ask, self.reply, self.req = await mb(int, int)


class MailBoxAskReply(MailBoxBaseSetup.SetupChan):
    async def test_1(self) -> None:
        create_task(echo(self.ask, reply=self.reply, cycles=1))
        ans = await self.req(1)
        self.assertEqual(ans, 1)
