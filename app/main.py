import sys
from pathlib import Path

from aiohttp import web

sys.path.append(str(Path(__file__).parent.parent))

from app.settings import START_WITH_WEBHOOK, WEBAPP_HOST, WEBAPP_PORT
from core.application import Application


async def create_app() -> web.Application:
    application = Application()
    return application.create_app()


if __name__ == '__main__':

    application = Application()
    app = application.create_app()

    if START_WITH_WEBHOOK:
        web.run_app(app=app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        application.bot_polling()
