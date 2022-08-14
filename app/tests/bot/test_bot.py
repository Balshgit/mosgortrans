import pytest
from aiogram import Bot, types
from aiogram.dispatcher.filters.builtin import Command
from app.core.bot import dispatcher
from app.tests.conftest import FakeTelegram
from app.tests.data.factories import UserFactory

pytestmark = [
    pytest.mark.asyncio,
]


async def test_parse_site(bot: Bot) -> None:
    tg_user = UserFactory().as_dict()
    user = types.User(**tg_user)

    async with FakeTelegram(message_data=tg_user):
        result = await bot.me

    assert result == user


async def test_command1(bot: Bot) -> None:

    dispatcher.bot = bot
    handlers = dispatcher.message_handlers.handlers
    for handler in handlers:
        handl = list(
            filter(lambda obj: isinstance(obj.filter, Command), handler.filters)
        )
        if handl:
            command = handl[0].filter.commands[0]
            assert command
