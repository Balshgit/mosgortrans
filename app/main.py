from aiogram import Dispatcher
from aiogram.utils.executor import start_polling, start_webhook
from core.bot import bot, dispatcher
from core.logger import logger
from core.scheduler import asyncio_schedule
from settings import (
    START_WITH_WEBHOOK,
    WEBAPP_HOST,
    WEBAPP_PORT,
    WEBHOOK_PATH,
    WEBHOOK_URL,
)


async def on_startup(dp: Dispatcher) -> None:
    await bot.set_webhook(WEBHOOK_URL)
    asyncio_schedule()


async def on_shutdown(dp: Dispatcher) -> None:
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.warning('Bye!')


def bot_polling() -> None:
    logger.info("Start bot in polling mode")
    start_polling(
        dispatcher=dispatcher,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )


def bot_webhook() -> None:
    logger.info("Start bot with webhook")
    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


if __name__ == '__main__':
    if START_WITH_WEBHOOK:
        bot_webhook()
    else:
        bot_polling()
