from http import HTTPStatus

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.utils.executor import start_polling
from aiohttp import web
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


async def bot_startup() -> None:
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f'Webhook set to {WEBHOOK_URL}')
    asyncio_schedule()


async def bot_shutdown() -> None:
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

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
    logger.info(data)
    tg_update = Update(**data)

    Dispatcher.set_current(dispatcher)
    Bot.set_current(dispatcher.bot)

    await dispatcher.process_update(tg_update)

    return web.Response(status=HTTPStatus.OK)


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
