from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage, get_new_configured_app
from aiogram.utils.executor import start_webhook, Executor

from mos_gor import logger, parse_site, download_gecko_driver, configure_firefox_driver
from settings import API_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

from aiohttp import web

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler()
async def echo(message: types.Message):
    # Regular request
    # await bot.send_message(message.chat.id, message.text)

    text = parse_site(driver=driver)

    # or reply INTO webhook
    return SendMessage(message.chat.id, text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logger.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.warning('Bye!')


async def async_app():
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
    executor = Executor(dp, skip_updates=True)
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
    executor._prepare_webhook(WEBHOOK_PATH, app=app)
    await executor._startup_webhook()
    return app


if __name__ == '__main__':
    import uvicorn
    download_gecko_driver()
    driver = configure_firefox_driver()

    uvicorn.run(async_app(), host=WEBAPP_HOST, port=WEBAPP_PORT)

    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # )
