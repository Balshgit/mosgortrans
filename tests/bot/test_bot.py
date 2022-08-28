import os
import time
from unittest import mock

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
            'from': {
                'id': 417070387,
                'is_bot': False,
                'first_name': 'Dmitry',
                'last_name': 'Afanasyev',
                'username': 'Balshtg',
                'language_code': 'en',
            },
            'chat': {
                'id': 417070387,
                'first_name': 'Dmitry',
                'last_name': 'Afanasyev',
                'username': 'Balshtg',
                'type': 'private',
            },
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


@pytest.mark.skipif(
    bool(os.environ.get("LOCALTEST", False)) is False,
    reason="Schemathesis test will be skipped if environment var SCHEMATHESIS=1 is not set",
)
async def test_selenoid_text(dispatcher_fixture: Dispatcher) -> None:
    data = {
        'id': '1791303673263594560',
        'from': {
            'id': 417070387,
            'is_bot': False,
            'first_name': 'Dmitry',
            'last_name': 'Afanasyev',
            'username': 'Balshtg',
            'language_code': 'en',
        },
        'message': {
            'message_id': 1316,
            'from': {
                'id': 5494499556,
                'is_bot': False,
                'first_name': 'balshbot_transport',
                'username': 'balshbot_transport_bot',
            },
            'chat': {
                'id': 417070387,
                'first_name': 'Dmitry',
                'last_name': 'Afanasyev',
                'username': 'Balshtg',
                'type': 'private',
            },
            'date': 1661692626,
            'text': 'Остановка Б. Академическая ул, д. 15\n\nАвтобус 300 - прибывает\nАвтобус Т19 - 7 мин',
            'reply_markup': {
                'inline_keyboard': [
                    [
                        {
                            'text': 'Дом -> Офис',
                            'callback_data': 'station:home->office',
                        },
                        {
                            'text': 'Офис -> Дом',
                            'callback_data': 'station:office->home',
                        },
                    ]
                ]
            },
        },
        'chat_instance': '-6044557427944557947',
        'data': 'station:home->office',
    }
    TransportBot.bot = dispatcher_fixture.bot

    # @mock.patch('app.core.bot.TransportBot.bot.send_message')
    with mock.patch(
        'app.core.bot.TransportBot.bot.send_message',
        return_value=data['message']['chat'],  # type: ignore
    ):
        async with FakeTelegram(message_data=data):
            call_back = types.CallbackQuery(**data)
            result = await TransportBot.home_office(query=call_back, callback_data={})
            assert result == data['message']['chat']  # type: ignore
