import asyncio

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook

from mos_gor import logger, parse_site, download_gecko_driver, configure_firefox_driver
from settings import API_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['chatid'])
async def chat_id(message: types.Message) -> SendMessage:

    # or reply INTO webhook
    return SendMessage(message.chat.id, message.chat.id)


@dp.message_handler()
async def echo(message: types.Message) -> SendMessage:
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    text = parse_site(driver=driver)

    # or reply INTO webhook
    return SendMessage(message.chat.id, text)


async def send_message(chat_ids: list[int]):
    text = parse_site(driver=driver)

    await asyncio.gather(
        *[bot.send_message(chat_id=chat_id, text=text, parse_mode=types.ParseMode.HTML) for chat_id in chat_ids]
    )


def asyncio_schedule() -> None:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    kwargs = {'chat_ids': [417070387, ]}

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_message, kwargs=kwargs,
                      trigger='cron', day_of_week='mon-fri', hour=19, minute=32, second=10)
    scheduler.add_job(send_message, kwargs=kwargs,
                      trigger='cron', day_of_week='mon-fri', hour=19, minute=37, second=20)
    scheduler.add_job(send_message, kwargs=kwargs,
                      trigger='cron', day_of_week='mon-fri', hour=19, minute=42, second=42)
    scheduler.start()


async def on_startup(dp) -> None:
    await bot.set_webhook(WEBHOOK_URL)
    asyncio_schedule()


async def on_shutdown(dp):
    logger.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.warning('Bye!')


if __name__ == '__main__':
    download_gecko_driver()
    driver = configure_firefox_driver()

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
