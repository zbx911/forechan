from typing import Protocol
from unittest import IsolatedAsyncioTestCase

from ...forechan.types import Buf
from ..da import extract_testcases


class HasBuf(Protocol):
    buf: Buf[int]


class BaseCases:
    class TypeConformance(IsolatedAsyncioTestCase, HasBuf):
        async def test_1(self) -> None:
            self.assertIsInstance(self.buf, Buf)


BASE_CASES = tuple(extract_testcases(BaseCases))
