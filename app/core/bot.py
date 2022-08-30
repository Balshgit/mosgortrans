import asyncio
from dataclasses import dataclass

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from app.core.parse_web import WebParser
from app.settings import TELEGRAM_API_TOKEN


@dataclass
class TransportBot:
    bot: Bot = Bot(TELEGRAM_API_TOKEN)
    dispatcher: Dispatcher = Dispatcher(bot)
    dispatcher.middleware.setup(LoggingMiddleware())
    stations_cb: CallbackData = CallbackData('station', 'direction')

    @staticmethod
    @dispatcher.message_handler(commands=['chatid'])
    async def chat_id(message: types.Message) -> types.Message:
        return await TransportBot.bot.send_message(message.chat.id, message.chat.id)

    @staticmethod
    def get_keyboard() -> types.InlineKeyboardMarkup:
        """
        Generate keyboard with list of posts
        """
        markup = types.InlineKeyboardMarkup()

        markup.row(
            types.InlineKeyboardButton(
                'Дом -> Офис',
                callback_data=TransportBot.stations_cb.new(direction='home->office'),
            ),
            types.InlineKeyboardButton(
                'Офис -> Дом',
                callback_data=TransportBot.stations_cb.new(direction='office->home'),
            ),
        )
        return markup

    @staticmethod
    @dispatcher.callback_query_handler(stations_cb.filter(direction='home->office'))
    async def home_office(
        query: types.CallbackQuery, callback_data: dict[str, str]
    ) -> types.Message:
        driver = WebParser.get_driver()
        text = WebParser.parse_yandex_maps(
            driver=driver,
            url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/?ll=37.527924%2C55.823470&tab=overview&z=21',
            message='Остановка Б. Академическая ул, д. 15',
            buses=[
                '300',
                'т19',
            ],
        )

        return await TransportBot.bot.send_message(
            query.message.chat.id, text, reply_markup=TransportBot.get_keyboard()
        )

    @staticmethod
    @dispatcher.callback_query_handler(stations_cb.filter(direction='office->home'))
    async def office_home(
        query: types.CallbackQuery, callback_data: dict[str, str]
    ) -> types.Message:
        driver = WebParser.get_driver()
        text = WebParser.parse_yandex_maps(
            driver=driver,
            url='https://yandex.ru/maps/213/moscow/stops/stop__9640288/?ll=37.505402%2C55.800214&tab=overview&z=21',
            message='Остановка Улица Алабяна',
            buses=[
                '300',
                'т19',
            ],
        )

        return await TransportBot.bot.send_message(
            query.message.chat.id, text, reply_markup=TransportBot.get_keyboard()
        )

    @staticmethod
    @dispatcher.message_handler()
    async def echo(message: types.Message) -> types.Message:
        return await TransportBot.bot.send_message(
            message.chat.id,
            'Выбери остановку',
            reply_markup=TransportBot.get_keyboard(),
        )

    @staticmethod
    async def morning_bus_mailing(chat_ids: list[int] | None) -> None:
        if not chat_ids:
            return None

        driver = WebParser.get_driver()
        text = WebParser.parse_yandex_maps(
            driver=driver,
            url='https://yandex.ru/maps/213/moscow/stops/stop__9640740/?ll=37.527924%2C55.823470&tab=overview&z=21',
            message='Остановка Б. Академическая ул, д. 15',
            buses=[
                '300',
                'т19',
            ],
        )
        await asyncio.gather(
            *[
                TransportBot.bot.send_message(
                    chat_id=chat_id, text=text, parse_mode=types.ParseMode.HTML
                )
                for chat_id in chat_ids
            ]
        )
