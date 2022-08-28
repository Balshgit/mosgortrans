from pathlib import Path

from decouple import AutoConfig

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = Path(__file__).parent

# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
env_path = BASE_DIR.joinpath('config')

config = AutoConfig(search_path=env_path)


GECKO_DRIVER_VERSION = config('GECKO_DRIVER_VERSION', default='0.31.0')

TELEGRAM_API_TOKEN = config(
    'TELEGRAM_API_TOKEN', default='123456789:AABBCCDDEEFFaabbccddeeff-1234567890'
)

# webhook settings
WEBHOOK_HOST = config('WEBHOOK_HOST', default='')
WEBHOOK_PATH = config('WEBHOOK_PATH', default='')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}/{TELEGRAM_API_TOKEN}"

# webserver settings
WEBAPP_HOST = config('WEBAPP_HOST', default='127.0.0.1')  # or ip
WEBAPP_PORT = config('WEBAPP_PORT', cast=int, default=8084)

START_WITH_WEBHOOK = config('START_WITH_WEBHOOK', cast=bool, default=False)

DRIVER_SESSION_TTL = 28  # selenium driver session cache ttl in seconds
