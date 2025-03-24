from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag
import json
import time
from typing import List, override

from web_scraper import WebScraper, Config
from log import Log


def conv_chrome_options(
    chrome_options: List[str], experimental_options: List[tuple], arguments: List[str]
) -> Options:
    result = Options()
    for option in chrome_options:
        result.add_argument(option)
    for option in experimental_options:
        result.add_experimental_option(*option)
    for argument in arguments:
        result.add_argument(argument)
    return result


class TiktokConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.chrome_options = [
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        self.experimental_options = [
            (
                "excludeSwitches",
                ["enable-automation"],
            ),
            ("useAutomationExtension", False),
        ]
        self.arguments = [
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]


class TiktokScraper(WebScraper):
    def __init__(self, config: TiktokConfig) -> None:
        self.starttime = time.time()
        super().__init__(config)
        chrome_options = conv_chrome_options(
            config.chrome_options, config.experimental_options, config.arguments
        )
        self.driver = webdriver.Chrome(options=chrome_options)

    @override
    def run(self, urls: List[str]) -> None:
        for url in urls:
            self.get_information(url)
        endtime = time.time()
        Log.info(f"Total time taken: {endtime - self.starttime}")

    @override
    def close(self) -> None:
        self.driver.quit()

    def get_information(self, url):
        try:
            self.driver.get(url)

            # Use explicit wait instead of fixed sleep
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "script"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

            if isinstance(script_tag, Tag):
                caption = script_tag.string
                if not caption:
                    caption = script_tag.text
                json_data = json.loads(caption)
                user_info = (
                    json_data.get("__DEFAULT_SCOPE__", {})
                    .get("webapp.user-detail", {})
                    .get("userInfo", {})
                )

                if user_info:
                    videos = []
                    for video_div in soup.select("div[data-e2e='user-post-item']"):
                        caption = None
                        likes = None
                        caption_tag = video_div.select_one(
                            "div[data-e2e='video-title']"
                        )
                        likes_tag = video_div.select_one(
                            "strong[data-e2e='video-views']"
                        )
                        if isinstance(caption_tag, Tag):
                            caption = caption_tag.text.strip()
                        if isinstance(likes_tag, Tag):
                            likes = likes_tag.text.strip()
                        video = {
                            "video_id": video_div.get("data-video-id"),
                            "caption": caption,
                            "likes": likes,
                            "url": f"https://www.tiktok.com/@{user_info['user']['uniqueId']}/video/{video_div.get('data-video-id')}",
                        }
                        videos.append(video)
                    user_info["videos"] = videos
                    self.result.append(user_info)
                    print(f"Success: {url}")
                    return
            print(f"No data found: {url}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")


# EOF
