import asyncio
import sys
from http import HTTPStatus
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.utils.executor import start_polling
from aiohttp import web

sys.path.append(str(Path(__file__).parent.parent))

from app.core.bot import bot, dispatcher
from app.core.logger import logger
from app.core.scheduler import asyncio_schedule
from app.settings import (
    API_TOKEN,
    START_WITH_WEBHOOK,
    WEBAPP_HOST,
    WEBAPP_PORT,
    WEBHOOK_PATH,
    WEBHOOK_URL,
)

queue: asyncio.Queue = asyncio.Queue()  # type: ignore


async def bot_startup() -> None:
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f'Webhook set to {WEBHOOK_URL}'.replace(API_TOKEN, '{BOT_API_TOKEN}'))
    asyncio_schedule()
    await worker()


async def bot_shutdown() -> None:
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

    session = await bot.get_session()
    if session and not session.closed:
        await session.close()
        await asyncio.sleep(0.2)

    logger.warning('Bye!')


async def aiogram_startup(dp: Dispatcher) -> None:
    await bot_startup()


async def aiogram_shutdown(dp: Dispatcher) -> None:
    await bot_shutdown()


async def on_startup_gunicorn(app: web.Application) -> None:
    logger.info("Start bot with webhook")
    await bot_startup()


async def on_shutdown_gunicorn(app: web.Application) -> None:
    await bot_shutdown()


def bot_polling() -> None:
    logger.info("Start bot in polling mode")
    start_polling(
        dispatcher=dispatcher,
        skip_updates=True,
        on_startup=aiogram_startup,
        on_shutdown=aiogram_shutdown,
    )


async def webhook(request: web.Request) -> web.Response:
    """
    Listen {WEBHOOK_PATH} and proxy post request to bot

    :param request:
    :return:
    """
    data = await request.json()
    tg_update = Update(**data)
    logger.info(tg_update)
    queue.put_nowait(tg_update)
    logger.info('Put in queue')
    return web.Response(status=HTTPStatus.ACCEPTED)


async def worker() -> None:
    Dispatcher.set_current(dispatcher)
    Bot.set_current(dispatcher.bot)

    while True:
        await asyncio.sleep(1)
        update = await queue.get()
        logger.warning(f"Get update {update}")
        await dispatcher.process_update(update)


async def create_app() -> web.Application:
    application = web.Application()
    application.router.add_post(f'{WEBHOOK_PATH}/{API_TOKEN}', webhook)
    application.on_startup.append(on_startup_gunicorn)
    application.on_shutdown.append(on_shutdown_gunicorn)
    return application


if __name__ == '__main__':

    if START_WITH_WEBHOOK:
        app = create_app()
        web.run_app(app=app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        bot_polling()
