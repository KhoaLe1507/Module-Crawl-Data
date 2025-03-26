from src.scraper.web_scraper import ScrapeConfig


class InstagramConfig(ScrapeConfig):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "instagram"
        self.data_type = "profile"
