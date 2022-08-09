import os
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path

import wget
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox import options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver

from settings import BASE_DIR, GECKO_DRIVER_VERSION

logger.remove()
logger.add(sink=sys.stdout, colorize=True, level='DEBUG',
           format="<cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan> | <level>{level}</level> | "
                  "<magenta>{message}</magenta>")


def download_gecko_driver():
    gecko_driver = f'https://github.com/mozilla/geckodriver/releases/download/v{GECKO_DRIVER_VERSION}/' \
                   f'geckodriver-v{GECKO_DRIVER_VERSION}-linux64.tar.gz'

    if not Path(f'{BASE_DIR}/geckodriver').exists():
        logger.info(f'Downloading gecodriver v {GECKO_DRIVER_VERSION}...')
        geckodriver_file = wget.download(url=gecko_driver, out=BASE_DIR)

        with tarfile.open(geckodriver_file) as tar:
            tar.extractall(BASE_DIR)
        os.remove(f'{BASE_DIR}/geckodriver-v{GECKO_DRIVER_VERSION}-linux64.tar.gz')
        logger.info(f'\ngeckodriver has been downloaded to folder {BASE_DIR}')


def configure_firefox_driver(private_window: bool = False) -> WebDriver:
    opt = options.Options()
    opt.headless = True
    opt.add_argument('-profile')
    opt.add_argument(f'{Path.home()}/snap/firefox/common/.mozilla/firefox')
    if private_window:
        opt.set_preference("browser.privatebrowsing.autostart", True)
    service = Service(executable_path=f'{BASE_DIR}/geckodriver')
    firefox_driver = webdriver.Firefox(service=service, options=opt)

    return firefox_driver


def parse_site(driver: WebDriver, url: str, message: str) -> str:
    driver.get(url)
    time.sleep(4)
    elements = driver.find_elements(by='class name', value='masstransit-vehicle-snippet-view')

    bus_300, bus_t19 = None, None
    bus_300_arrival, bus_t19_arrival = None, None

    for element in elements:
        try:
            bus_300 = element.find_element(by='css selector', value='[aria-label="300"]')
            bus_300_arrival = element.find_element(by='class name', value='masstransit-prognoses-view__title-text')
        except NoSuchElementException:
            pass
        try:
            bus_t19 = element.find_element(by='css selector', value='[aria-label="т19"]')
            bus_t19_arrival = element.find_element(by='class name', value='masstransit-prognoses-view__title-text')
        except NoSuchElementException:
            pass
    answer = f'{message}\n\n'
    if not all([bus_300, bus_t19]):
        return 'Автобусов 300 или Т19 не найдено. \n\nСмотри на карте :)'
    if bus_300:
        answer += f'Автобус {bus_300.text} - {bus_300_arrival.text}\n'
    if bus_t19:
        answer += f'Автобус {bus_t19.text} - {bus_t19_arrival.text}'
    return answer
