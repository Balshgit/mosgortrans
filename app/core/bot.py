import asyncio

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from app.core.parse_web import get_driver, parse_site
from app.settings import TELEGRAM_API_TOKEN

bot = Bot(token=TELEGRAM_API_TOKEN)
dispatcher = Dispatcher(bot)
dispatcher.middleware.setup(LoggingMiddleware())


stations_cb = CallbackData('station', 'direction')


def get_keyboard() -> types.InlineKeyboardMarkup:
    """
    Generate keyboard with list of posts
    """
    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            'Дом -> Офис', callback_data=stations_cb.new(direction='home->office')
        ),
        types.InlineKeyboardButton(
            'Офис -> Дом', callback_data=stations_cb.new(direction='office->home')
        ),
    )
    return markup


@dispatcher.callback_query_handler(stations_cb.filter(direction='home->office'))
async def home_office(
    query: types.CallbackQuery, callback_data: dict[str, str]
) -> types.Message:
    driver = get_driver()

    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/'
        '?l=masstransit&ll=37.527754%2C55.823507&tab=overview&z=21',
        message='Остановка Б. Академическая ул, д. 15',
    )

    return await bot.send_message(
        query.message.chat.id, text, reply_markup=get_keyboard()
    )


@dispatcher.callback_query_handler(stations_cb.filter(direction='office->home'))
async def office_home(
    query: types.CallbackQuery, callback_data: dict[str, str]
) -> types.Message:
    driver = get_driver()
    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640288/?'
        'l=masstransit&ll=37.505338%2C55.800160&tab=overview&z=211',
        message='Остановка Улица Алабяна',
    )

    return await bot.send_message(
        query.message.chat.id, text, reply_markup=get_keyboard()
    )


@dispatcher.message_handler(commands=['chatid'])
async def chat_id(message: types.Message) -> types.Message:
    return await bot.send_message(message.chat.id, message.chat.id)


@dispatcher.message_handler()
async def echo(message: types.Message) -> types.Message:
    return await bot.send_message(
        message.chat.id, 'Выбери остановку', reply_markup=get_keyboard()
    )


async def morning_bus_mailing(chat_ids: list[int]) -> None:
    driver = get_driver()
    text = parse_site(
        driver=driver,
        url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/'
        '?l=masstransit&ll=37.527754%2C55.823507&tab=overview&z=21',
        message='Остановка Б. Академическая ул, д. 15',
    )
    await asyncio.gather(
        *[
            bot.send_message(
                chat_id=chat_id, text=text, parse_mode=types.ParseMode.HTML
            )
            for chat_id in chat_ids
        ]
    )
