import os
import tarfile
import time
from collections import defaultdict
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


class WebParser:
    @staticmethod
    def download_gecko_driver() -> None:
        gecko_driver_url = (
            f'https://github.com/mozilla/geckodriver/releases/download/v{GECKO_DRIVER_VERSION}/'
            f'geckodriver-v{GECKO_DRIVER_VERSION}-linux64.tar.gz'
        )

        if not Path(BASE_DIR / 'geckodriver').exists():
            logger.info(f'Downloading gecodriver v {GECKO_DRIVER_VERSION}...')
            geckodriver_file = wget.download(
                url=gecko_driver_url, out=BASE_DIR.resolve().as_posix()
            )

            with tarfile.open(geckodriver_file) as tar:
                tar.extractall(BASE_DIR)
            os.remove(
                f'{BASE_DIR / "geckodriver"}-v{GECKO_DRIVER_VERSION}-linux64.tar.gz'
            )
            logger.info(f'\ngeckodriver has been downloaded to folder {BASE_DIR}')

    @staticmethod
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

    @staticmethod
    def parse_yandex_maps(
        *,
        url: str,
        message: str,
        buses: list[str],
        driver: RemoteWebDriver | None = None,
    ) -> str:
        if not driver:
            logger.error('Driver is not configured')
            return '??????-???? ?????????? ???? ??????. :( ?????????????? Firefox ???? ??????????????????????????????.'

        driver.get(url)
        time.sleep(1)

        bus_arrival: dict[str, str | None] = defaultdict(str)

        try:
            web_elements = driver.find_elements(
                by='class name', value='masstransit-vehicle-snippet-view'
            )
            for web_element in web_elements:
                bus = web_element.find_element(
                    by='class name', value='masstransit-vehicle-snippet-view__main-text'
                )
                if bus:
                    bus_arrival_time = web_element.find_element(
                        by='class name',
                        value='masstransit-prognoses-view__title-text',
                    )
                    bus_arrival[bus.text] = (
                        bus_arrival_time.text if bus_arrival_time else None
                    )
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass

        if not any([bus_arrival.get(bus_name) for bus_name in buses]):
            return f'?????????????????? {", ".join(buses)} ???? ??????????????. \n\n???????????? ???? ?????????? :)'

        answer = f'{message}\n\n'
        for bus_name in buses:
            arrival_time = bus_arrival.get(bus_name)
            if arrival_time:
                answer += f'?????????????? {bus_name} - {arrival_time}\n'
        return answer

    @staticmethod
    @timed_cache(seconds=DRIVER_SESSION_TTL)
    def get_driver() -> RemoteWebDriver:
        opt = options.Options()
        opt.headless = True
        driver = RemoteWebDriver(
            command_executor='http://selenoid_host:4444/wd/hub', options=opt
        )
        return driver
