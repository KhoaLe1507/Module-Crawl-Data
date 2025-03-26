from src.scraper.web_scraper import WebScraper
import time
import random
from tqdm import tqdm
import httpx

from typing import override, List
from src.instagram.config import InstagramConfig
from src.instagram.utils import scrape_user_fallback, parse_user
from src.utils.log import Log


class InstagramScraper(WebScraper):
    def __init__(self, config: InstagramConfig) -> None:
        super().__init__(config)
        self.client = httpx.Client(
            headers={
                "x-ig-app-id": "936619743392459",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
            }
        )

    @override
    def run__(self, urls: List[str]) -> None:
        for url in tqdm(urls):
            username = url.strip().rstrip("/").split("/")[-1]
            try:
                # Thực hiện cào dữ liệu
                Log.info(f"Đang xử lí username: {username}")
                user_data = scrape_user_fallback(self.client, username)
                parsed_data = parse_user(user_data)
                self.result.append(parsed_data)
                print(parsed_data)
                Log.info(f"Đã lưu dữ liệu cho: {username}")
                delay = random.uniform(20, 30)
                Log.info(f"Delay: {delay:.2f} giây")
                time.sleep(delay)
            except Exception as e:
                # Khi gặp lỗi (ví dụ bị chặn) thì in lỗi và dừng chương trình
                Log.error(f"Lỗi khi cào dữ liệu của {username}: {e}")
                break


# EOF
