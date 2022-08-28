import time

import pytest
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.types import Update
from app.core.bot import TransportBot
from tests.conftest import FakeTelegram
from tests.data.factories import ChatFactory, UserFactory

pytestmark = [
    pytest.mark.asyncio,
]


async def test_get_me_from_bot(bot: Bot) -> None:
    tg_user = UserFactory()._asdict()
    user = types.User(**tg_user)

    async with FakeTelegram(message_data=tg_user):
        result = await bot.me

    assert result == user


async def test_command1(bot: Bot) -> None:

    TransportBot.dispatcher.bot = bot
    handlers = TransportBot.dispatcher.message_handlers.handlers
    commands = []
    for handler in handlers:
        handl = list(
            filter(lambda obj: isinstance(obj.filter, Command), handler.filters)
        )
        if handl:
            commands.append(handl[0].filter.commands[0])
    assert commands == ['chatid']


async def test_update(dispatcher_fixture: Dispatcher) -> None:

    data = {
        'update_id': 957250703,
        'message': {
            'message_id': 417070387,
            'from': UserFactory()._asdict(),
            'chat': ChatFactory()._asdict(),
            'date': time.time(),
            'text': '/chatid',
            'entities': [{'type': 'bot_command', 'offset': 0, 'length': 7}],
        },
    }
    TransportBot.bot = dispatcher_fixture.bot

    async with FakeTelegram(message_data=data):
        update = Update(**data)
        result = await TransportBot.echo(update.message)
        assert result == types.Message(**data)
