from typing import List
from src.scraper.config import ScrapeConfig
from src.utils.file import get_lines, export_json


class WebScraper(object):
    def __init__(self, config: ScrapeConfig) -> None:
        config.check()
        self.config = config
        self.result: List = []

    def run(self) -> None:
        urls = get_lines(f"{ScrapeConfig.input_folder}/{self.config.platform}_urls.txt")
        self.run__(urls)
        export_json(
            self.result,
            ScrapeConfig.output_folder,
            self.config.platform,
            self.config.data_type,
        )

    def run__(self, urls: List[str]) -> None:
        _ = urls

    def close(self) -> None:
        pass


# EOF
