import pytest
from aiogram import Bot, types
from app.tests.conftest import FakeTelegram
from app.tests.dataset import USER

pytestmark = [
    pytest.mark.asyncio,
]


async def test_parse_site(bot: Bot) -> None:
    user = types.User(**USER)

    async with FakeTelegram(message_data=USER):
        result = await bot.me

    assert result == user
