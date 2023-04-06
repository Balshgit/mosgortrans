import time
from collections import defaultdict

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.utils import logger, timed_cache
from app.settings import DRIVER_SESSION_TTL


class WebParser:
    @staticmethod
    def parse_yandex_maps(
        *,
        url: str,
        message: str,
        buses: list[str],
        driver: WebDriver | None = None,
    ) -> str:
        if not driver:
            logger.error('Driver is not configured')
            return 'Что-то пошло не так. :( Драйвер Firefox не сконфигурирован.'

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
            return f'Автобусов {", ".join(buses)} не найдено. \n\nСмотри на карте :)'

        answer = f'{message}\n\n'
        for bus_name in buses:
            arrival_time = bus_arrival.get(bus_name)
            if arrival_time:
                answer += f'Автобус {bus_name} - {arrival_time}\n'
        return answer

    @staticmethod
    @timed_cache(seconds=DRIVER_SESSION_TTL)
    def get_driver() -> WebDriver:
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        driver = webdriver.Remote(
            command_executor='http://selenoid_host:4444/wd/hub', options=opt
        )
        return driver
