import asyncio
from dataclasses import dataclass

from aiogram import Dispatcher
from aiogram.utils.executor import start_polling
from aiohttp import web

from app.core.bot import TransportBot
from app.core.routes import Handler
from app.core.scheduler import BotScheduler, bot_scheduler
from app.core.utils import logger
from app.settings import TELEGRAM_API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL


@dataclass
class Application:
    handler: Handler = Handler()
    scheduler: BotScheduler = bot_scheduler

    async def _on_startup(self, dp: Dispatcher) -> None:
        logger.info("Start bot with webhook")
        await TransportBot.bot.set_webhook(WEBHOOK_URL)
        loop = asyncio.get_running_loop()
        loop.create_task(self.handler.get_updates_from_queue())
        logger.info(
            f'Webhook set to {WEBHOOK_URL}'.replace(
                TELEGRAM_API_TOKEN, '{TELEGRAM_API_TOKEN}'
            )
        )
        self.scheduler.start()

    async def _on_shutdown(self, dp: Dispatcher) -> None:
        logger.warning('Shutting down..')

        # Remove webhook (not acceptable in some cases)
        await TransportBot.bot.delete_webhook()

        session = await TransportBot.bot.get_session()
        if session and not session.closed:
            await session.close()
            await asyncio.sleep(0)

        logger.warning('Bye!')

    @staticmethod
    def bot_polling() -> None:
        logger.info("Start bot in polling mode")
        start_polling(
            dispatcher=TransportBot.dispatcher,
            skip_updates=True,
        )

    def create_app(self) -> web.Application:
        app = web.Application()
        app.add_routes(
            [
                web.get(f'{WEBHOOK_PATH}/', self.handler.health_check),
                web.post(
                    f'{WEBHOOK_PATH}/{TELEGRAM_API_TOKEN}',
                    self.handler.put_updates_on_queue,
                ),
            ]
        )
        app.on_startup.append(self._on_startup)
        app.on_shutdown.append(self._on_shutdown)
        return app
