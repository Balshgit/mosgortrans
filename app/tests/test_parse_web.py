import pytest
from aiogram import Bot, types
from app.tests.conftest import FakeTelegram
from app.tests.factories import UserFactory

pytestmark = [
    pytest.mark.asyncio,
]


async def test_parse_site(bot: Bot) -> None:
    tg_user = UserFactory().as_dict()
    user = types.User(**tg_user)

    async with FakeTelegram(message_data=tg_user):
        result = await bot.me

    assert result == user
