import asyncio

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.executor import start_webhook

from mos_gor import logger, parse_site, download_gecko_driver, configure_firefox_driver
from settings import API_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)
dispatcher.middleware.setup(LoggingMiddleware())

cron_jobs = [
        {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 8, 'minute': 59, 'second': 0},
        {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 4, 'second': 0},
        {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 9, 'second': 0},
    ]

user_chat_ids = {'chat_ids': [417070387,  # me
                              431571617,  # Lenok
                              ]}


stations_cb = CallbackData('station', 'direction')


def get_keyboard() -> types.InlineKeyboardMarkup:
    """
    Generate keyboard with list of posts
    """
    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton('Дом -> Офис', callback_data=stations_cb.new(direction='home->office')),
        types.InlineKeyboardButton('Офис -> Дом', callback_data=stations_cb.new(direction='office->home')),
    )
    return markup


@dispatcher.callback_query_handler(stations_cb.filter(direction='home->office'))
async def home_office(query: types.CallbackQuery, callback_data: dict[str, str]) -> None:

    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/'
            '?l=masstransit&ll=37.527754%2C55.823507&tab=overview&z=21',
        message='Остановка Б. Академическая ул, д. 15'
    )

    # or reply INTO webhook
    return await query.message.edit_text(text, reply_markup=get_keyboard())


@dispatcher.callback_query_handler(stations_cb.filter(direction='office->home'))
async def office_home(query: types.CallbackQuery, callback_data: dict[str, str]) -> Message:

    # or reply INTO webhook
    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640288/?'
            'l=masstransit&ll=37.505338%2C55.800160&tab=overview&z=211',
        message='Остановка Улица Алабяна'
    )
    return await query.message.edit_text(text, reply_markup=get_keyboard())


@dispatcher.message_handler(commands=['chatid'])
async def chat_id(message: types.Message) -> SendMessage:

    # or reply INTO webhook
    return SendMessage(message.chat.id, message.chat.id)


@dispatcher.message_handler()
async def echo(message: types.Message) -> None:
    await message.reply('Выбери остановку', reply_markup=get_keyboard())


async def send_message(chat_ids: list[int]) -> None:
    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/'
            '?l=masstransit&ll=37.527754%2C55.823507&tab=overview&z=21',
        message='Остановка Б. Академическая ул, д. 15'
    )
    await asyncio.gather(
        *[bot.send_message(chat_id=chat_id, text=text, parse_mode=types.ParseMode.HTML) for chat_id in chat_ids]
    )


def asyncio_schedule() -> None:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    for cron in cron_jobs:
        scheduler.add_job(send_message, kwargs=user_chat_ids, **cron)
    scheduler.start()


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
    download_gecko_driver()
    driver = configure_firefox_driver()

    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
