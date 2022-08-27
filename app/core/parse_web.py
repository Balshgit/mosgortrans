import os
import tarfile
import time
from pathlib import Path

import wget
from app.core.utils import logger, timed_cache
from app.settings import BASE_DIR, DRIVER_SESSION_TTL, GECKO_DRIVER_VERSION
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.firefox import options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import RemoteWebDriver, WebDriver


def download_gecko_driver() -> None:
    gecko_driver = (
        f'https://github.com/mozilla/geckodriver/releases/download/v{GECKO_DRIVER_VERSION}/'
        f'geckodriver-v{GECKO_DRIVER_VERSION}-linux64.tar.gz'
    )

    if not Path(BASE_DIR / 'geckodriver').exists():
        logger.info(f'Downloading gecodriver v {GECKO_DRIVER_VERSION}...')
        geckodriver_file = wget.download(
            url=gecko_driver, out=BASE_DIR.resolve().as_posix()
        )

        with tarfile.open(geckodriver_file) as tar:
            tar.extractall(BASE_DIR)
        os.remove(f'{BASE_DIR / "geckodriver"}-v{GECKO_DRIVER_VERSION}-linux64.tar.gz')
        logger.info(f'\ngeckodriver has been downloaded to folder {BASE_DIR}')


def configure_firefox_driver(private_window: bool = False) -> WebDriver | None:
    opt = options.Options()
    opt.headless = True
    opt.add_argument('-profile')
    opt.add_argument(f'{Path.home()}/snap/firefox/common/.mozilla/firefox')
    if private_window:
        opt.set_preference("browser.privatebrowsing.autostart", True)
    service = Service(executable_path=(BASE_DIR / 'geckodriver').as_posix())
    try:
        firefox_driver = webdriver.Firefox(service=service, options=opt)
        return firefox_driver
    except WebDriverException:
        logger.error('Error configuring webdriver. Possible it already configured')
        return None


def parse_site(url: str, message: str, driver: RemoteWebDriver | None = None) -> str:
    if not driver:
        logger.error('Driver is not configured')
        return 'Что-то пошло не так. :( Драйвер Firefox не сконфигурирован.'
    driver.get(url)
    time.sleep(1)

    bus_300, bus_t19 = None, None
    bus_300_arrival, bus_t19_arrival = None, None

    elements = driver.find_elements(
        by='class name', value='masstransit-brief-schedule-view'
    )

    for element in elements:
        try:
            bus_300 = element.find_element(
                by='css selector', value='[aria-label="300"]'
            )
            bus_300_arrival = element.find_element(
                by='class name', value='masstransit-prognoses-view__title-text'
            )
            bus_t19 = element.find_element(
                by='css selector', value='[aria-label="т19"]'
            )
            bus_t19_arrival = element.find_element(
                by='class name', value='masstransit-prognoses-view__title-text'
            )
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
    no_bus_at_all = True
    answer = f'{message}\n\n'
    if bus_300 and bus_300_arrival:
        answer += f'Автобус {bus_300.text} - {bus_300_arrival.text}\n'
        no_bus_at_all = False
    if bus_t19 and bus_t19_arrival:
        answer += f'Автобус {bus_t19.text} - {bus_t19_arrival.text}'
        no_bus_at_all = False
    if not no_bus_at_all:
        return answer
    if no_bus_at_all:
        return 'Автобусов 300 или Т19 не найдено. \n\nСмотри на карте :)'


@timed_cache(seconds=DRIVER_SESSION_TTL)
def get_driver() -> RemoteWebDriver:
    opt = options.Options()
    opt.headless = True
    driver = RemoteWebDriver(
        command_executor='http://selenoid_host:4444/wd/hub', options=opt
    )
    return driver
