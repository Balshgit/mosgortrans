import time

import pytest
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import Update
from app.core.bot import TransportBot
from tests.conftest import FakeTelegram
from tests.data.factories import UserFactory

pytestmark = [
    pytest.mark.asyncio,
]


async def test_parse_yandex_maps(bot: Bot) -> None:
    tg_user = UserFactory().as_dict()
    user = types.User(**tg_user)

    async with FakeTelegram(message_data=tg_user):
        result = await bot.me

    assert result == user


async def test_command1(bot: Bot) -> None:

    TransportBot.dispatcher.bot = bot
    handlers = TransportBot.dispatcher.message_handlers.handlers
    for handler in handlers:
        handl = list(
            filter(lambda obj: isinstance(obj.filter, Command), handler.filters)
        )
        if handl:
            command = handl[0].filter.commands[0]
            assert command


async def test_update(dispatcher_fixture: Dispatcher, bot: Bot) -> None:

    data = {
        "update_id": 957250703,
        "message": {
            "message_id": 417070387,
            "from": {
                "id": 417070387,
                "is_bot": False,
                "first_name": "Dmitry",
                "last_name": "Afanasyev",
                "username": "Balshtg",
                "language_code": "en",
            },
            "chat": {
                "id": 417070387,
                "first_name": "Dmitry",
                "last_name": "Afanasyev",
                "username": "Balshtg",
                "type": "private",
            },
            "date": time.time(),
            "text": "/chatid",
            "entities": [{"type": "bot_command", "offset": 0, "length": 7}],
        },
    }
    async with FakeTelegram(message_data=data):
        update = Update(**data)
        dispatcher_fixture.message_handler()
        await dispatcher_fixture.process_update(update)
    assert True
