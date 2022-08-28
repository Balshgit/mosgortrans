import asyncio
from http import HTTPStatus

from aiogram.types import Update
from aiohttp import web
from app.core.bot import dispatcher


class Handler:
    def __init__(self) -> None:
        self.queue: asyncio.Queue = asyncio.Queue()  # type: ignore

    @staticmethod
    async def health_check(request: web.Request) -> web.Response:
        return web.Response(text='Health OK', status=HTTPStatus.OK)

    async def put_updates_on_queue(self, request: web.Request) -> web.Response:
        """
        Listen {WEBHOOK_PATH} and proxy post request to bot

        :param request:
        :return:
        """
        data = await request.json()
        tg_update = Update(**data)
        self.queue.put_nowait(tg_update)

        return web.Response(status=HTTPStatus.ACCEPTED)

    async def get_updates_from_queue(self) -> None:
        while True:
            update = await self.queue.get()
            await dispatcher.process_update(update)
            await asyncio.sleep(0.1)
