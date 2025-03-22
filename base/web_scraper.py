from dataclasses import dataclass
import os
import json
import threading
import queue
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor


def get_lines(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f.readlines()]

    return urls


def export_json(data: List[Dict], filepath: str) -> None:
    dirpath = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(dirpath, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def conv_chrome_options(
    chrome_options: List[str], experimental_options: List[tuple]
) -> webdriver.ChromeOptions:
    result = webdriver.ChromeOptions()
    for option in chrome_options:
        result.add_argument(option)
    for option in experimental_options:
        result.add_experimental_option(*option)
    return result


@dataclass
class Config:
    chrome_options = ["start-maximized"]
    experimental_options = [
        ("prefs", {"profile.default_content_setting_values.notifications": 2})
    ]
    n_workers: int = 1
    n_exceptional_workers: int = 1


class WebScraper(object):
    def __init__(self, config: Config) -> None:
        self.config = config
        self.lock = threading.Lock()
        self.driver_queue = queue.Queue()
        self.exceptional_driver_queue = queue.Queue()
        self.chrome_options = conv_chrome_options(
            config.chrome_options, config.experimental_options
        )
        self.result: List[Dict] = []

    def __setup(self):
        try:
            for _ in range(self.config.n_workers):
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.chrome_options,
                )
                self.driver_queue.put(driver)
            for _ in range(self.config.n_exceptional_workers):
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.chrome_options,
                )
                self.exceptional_driver_queue.put(driver)
            print("Started the drivers succesfully")
        except Exception as e:
            print("Starting the drivers failed")
            print("Error: ", e)

    def run(self, urls: List[str]) -> None:
        self.__setup()
        with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
            self._run(executor, urls)

    def _run(self, executor: ThreadPoolExecutor, urls: List[str]) -> None:
        _ = executor
        _ = urls

    def close(self) -> None:
        while not self.driver_queue.empty():
            self.driver_queue.get().quit()
