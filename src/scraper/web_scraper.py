from typing import List
from src.scraper.config import ScrapeConfig
from src.utils.config import Config
from src.utils.file import get_lines, export_json
from src.gcs.upload import upload_to_gcs


class WebScraper(object):
    def __init__(self, config: ScrapeConfig) -> None:
        config.check()
        self.config = config
        self.result: List = []

    def run(self) -> None:
        urls = get_lines(f"{Config.input_folder}/{self.config.platform}_urls.txt")
        self.run__(urls)
        output_filename = f"{Config.output_folder}/{self.config.platform}_{self.config.data_type}.json"
        export_json(self.result, output_filename)
        if Config.product_mode:
            upload_to_gcs(
                Config.bucket_name,
                output_filename,
                self.config.platform,
                self.config.data_type,
            )

    def run__(self, urls: List[str]) -> None:
        _ = urls

    def close(self) -> None:
        pass


# EOF
