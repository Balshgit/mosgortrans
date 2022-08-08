from pathlib import Path

from decouple import AutoConfig

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = Path(__file__).parent

# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
env_path = BASE_DIR.joinpath('config')

config = AutoConfig(search_path=env_path)


GECKO_DRIVER_VERSION = config('GECKO_DRIVER_VERSION')
BASE_DIR = Path(__file__).parent.resolve().as_posix()

API_TOKEN = config('API_TOKEN')

# webhook settings
WEBHOOK_HOST = config('WEBHOOK_HOST')
WEBHOOK_PATH = config('WEBHOOK_PATH')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = config('WEBAPP_HOST')  # or ip
WEBAPP_PORT = config('WEBAPP_PORT')
