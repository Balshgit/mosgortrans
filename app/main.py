import asyncio
import sys
from http import HTTPStatus
from pathlib import Path

from aiogram import Dispatcher
from aiogram.types import Update
from aiogram.utils.executor import start_polling
from aiohttp import web

sys.path.append(str(Path(__file__).parent.parent))

from app.core.bot import bot, dispatcher
from app.core.logger import logger
from app.core.scheduler import asyncio_schedule
from app.settings import (
    START_WITH_WEBHOOK,
    TELEGRAM_API_TOKEN,
    WEBAPP_HOST,
    WEBAPP_PORT,
    WEBHOOK_PATH,
    WEBHOOK_URL,
)

queue = asyncio.Queue()  # type: ignore


async def on_startup(dp: Dispatcher) -> None:
    logger.info("Start bot with webhook")
    await bot.set_webhook(WEBHOOK_URL)
    loop = asyncio.get_running_loop()
    loop.create_task(get_updates_from_queue())
    logger.info(
        f'Webhook set to {WEBHOOK_URL}'.replace(
            TELEGRAM_API_TOKEN, '{TELEGRAM_API_TOKEN}'
        )
    )
    asyncio_schedule()


async def on_shutdown(dp: Dispatcher) -> None:
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    session = await bot.get_session()
    if session and not session.closed:
        await session.close()
        await asyncio.sleep(0.2)

    logger.warning('Bye!')


def bot_polling() -> None:
    logger.info("Start bot in polling mode")
    start_polling(
        dispatcher=dispatcher,
        skip_updates=True,
    )


async def put_updates_on_queue(request: web.Request) -> web.Response:
    """
    Listen {WEBHOOK_PATH} and proxy post request to bot

    :param request:
    :return:
    """
    data = await request.json()
    tg_update = Update(**data)
    queue.put_nowait(tg_update)

    return web.Response(status=HTTPStatus.ACCEPTED)


async def get_updates_from_queue() -> None:

    while True:
        update = await queue.get()
        await dispatcher.process_update(update)
        await asyncio.sleep(0.1)


async def create_app() -> web.Application:
    application = web.Application()
    application.router.add_post(
        f'{WEBHOOK_PATH}/{TELEGRAM_API_TOKEN}', put_updates_on_queue
    )
    application.on_startup.append(on_startup)
    application.on_shutdown.append(on_shutdown)
    return application


if __name__ == '__main__':

    if START_WITH_WEBHOOK:
        app = create_app()
        web.run_app(app=app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        bot_polling()
