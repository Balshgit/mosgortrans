from aiogram.utils.executor import start_webhook

from core.bot import bot, dispatcher
from core.logger import logger
from core.scheduler import asyncio_schedule
from settings import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT


async def on_startup(dispatcher) -> None:
    await bot.set_webhook(WEBHOOK_URL)
    asyncio_schedule()


async def on_shutdown(dispatcher):
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

    logger.warning('Bye!')


if __name__ == '__main__':

    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
