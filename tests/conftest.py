import asyncio
from typing import Any

import aresponses
import pytest_asyncio
from aiogram import Bot, Dispatcher

BOT_ID = 123456789
TOKEN = f'{BOT_ID}:AABBCCDDEEFFaabbccddeeff-1234567890'


class FakeTelegram(aresponses.ResponsesMockServer):
    def __init__(
        self, message_data: dict[str, Any], bot: Bot = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._body, self._headers = self.parse_data(message_data)

        if isinstance(bot, Bot):
            Bot.set_current(bot)

    async def __aenter__(self) -> None:
        await super().__aenter__()
        _response = self.Response(
            text=self._body, headers=self._headers, status=200, reason='OK'
        )
        self.add(self.ANY, response=_response)

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if hasattr(self, 'monkeypatch'):
            self.monkeypatch.undo()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def parse_data(message_data: dict[str, Any]) -> tuple[str, dict[str, str]]:
        from aiogram.utils import json
        from aiogram.utils.payload import _normalize

        _body = '{"ok":true,"result":' + json.dumps(_normalize(message_data)) + '}'
        _headers = {
            'Server': 'nginx/1.12.2',
            'Date': 'Tue, 03 Apr 2018 16:59:54 GMT',
            'Content-Type': 'application/json',
            'Content-Length': str(len(_body)),
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Expose-Headers': 'Content-Length,Content-Type,Date,Server,Connection',
            'Strict-Transport-Security': 'max-age=31536000; includeSubdomains',
        }
        return _body, _headers


@pytest_asyncio.fixture(name='bot')
async def bot_fixture() -> Bot:
    """Bot fixture."""

    bot = Bot(TOKEN)
    yield bot
    session = await bot.get_session()
    if session and not session.closed:
        await session.close()
        await asyncio.sleep(0.2)


@pytest_asyncio.fixture()
async def dispatcher_fixture(bot: Bot) -> Dispatcher:
    """Dispatcher fixture."""

    dp = Dispatcher(bot)
    yield dp
    session = await bot.get_session()
    if session and not session.closed:
        await session.close()
        await asyncio.sleep(0.2)
