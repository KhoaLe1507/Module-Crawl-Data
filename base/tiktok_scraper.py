from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Tag
import json
import time
from typing import List, override

from web_scraper import ScrapeResult, WebScraper, Config
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
        # start: config for chrome options
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
        # end: config for chrome options


class TiktokVideo(ScrapeResult):
    def __init__(self) -> None:
        self.video_id: str | List[str] | None = None
        self.caption: str | None = None
        self.likes: str | None = None
        self.url: str | None = None
        super().__init__()


class TiktokKOL(ScrapeResult):
    def __init__(self) -> None:
        self.id: str | None = None
        self.shortId: str | None = None
        self.uniqueId: str | None = None
        self.nickname: str | None = None
        self.avatarLarger: str | None = None
        self.avatarMedium: str | None = None
        self.avatarThumb: str | None = None
        self.signature: str | None = None
        self.createTime: int | None = None
        self.verified: bool = False
        self.secUid: str | None = None
        self.ftc: bool | None = None
        self.relation: int | None = None
        self.openFavorite: bool | None = None
        self.commentSetting: int | None = None
        self.commerceUserInfo: dict = {}
        self.duetSetting: int | None = None
        self.stitchSetting: int | None = None
        self.privateAccount: bool | None = None
        self.secret: bool | None = None
        self.isADVirtual: bool | None = None
        self.roomId: str | None = None
        self.uniqueIdModifyTime: int | None = None
        self.ttSeller: bool | None = None
        self.region: str | None = None
        self.downloadSetting: int | None = None
        self.profileTab: dict = {}
        self.followingVisibility: int | None = None
        self.recommendReason: str | None = None
        self.nowInvitationCardUrl: str | None = None
        self.nickNameModifyTime: int | None = None
        self.isEmbedBanned: bool | None = None
        self.canExpPlaylist: bool | None = None
        self.profileEmbedPermission: int | None = None
        self.language: str | None = None
        self.eventList: List = []
        self.suggestAccountBind: bool | None = None
        self.isOrganization = 0

        self.followerCount: int | None = None
        self.followingCount: int | None = None
        self.heart: int | None = None
        self.heartCount: int | None = None
        self.videoCount: int | None = None
        self.diggCount: int | None = None
        self.friendCount: int | None = None
        self.videos: List[TiktokVideo] = []
        super().__init__()


class TiktokScraper(WebScraper):
    def __init__(self, config: TiktokConfig) -> None:
        super().__init__(config)
        chrome_options = conv_chrome_options(
            config.chrome_options, config.experimental_options, config.arguments
        )
        self.driver = webdriver.Chrome(options=chrome_options)

    @override
    def run(self, urls: List[str]) -> None:
        starttime = time.time()
        for url in urls:
            try:
                self.get_information(url)
            except Exception as e:
                Log.error(f"Error processing {url}: {str(e)}")
        endtime = time.time()
        Log.info(f"Total time taken: {endtime - starttime}")

    @override
    def close(self) -> None:
        self.driver.quit()

    def get_information(self, url):
        self.driver.get(url)

        # Use explicit wait instead of fixed sleep
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

        if not isinstance(script_tag, Tag):
            Log.info(f"No data found: {url}")
            return

        caption = script_tag.string
        if not caption:
            caption = script_tag.text
        json_data = json.loads(caption)
        user_info = (
            json_data.get("__DEFAULT_SCOPE__", {})
            .get("webapp.user-detail", {})
            .get("userInfo", {})
        )

        if not user_info:
            return

        kol = TiktokKOL()
        kol.assign_from_dict(user_info["user"])
        kol.assign_from_dict(user_info["stats"])
        # videos = []
        # for video_div in soup.select("div[data-e2e='user-post-item']"):
        #     caption = None
        #     likes = None
        #     caption_tag = video_div.select_one("div[data-e2e='video-title']")
        #     likes_tag = video_div.select_one("strong[data-e2e='video-views']")
        #     if isinstance(caption_tag, Tag):
        #         caption = caption_tag.text.strip()
        #     if isinstance(likes_tag, Tag):
        #         likes = likes_tag.text.strip()
        #
        #     video = TiktokVideo()
        #     video.video_id = video_div.get("data-video-id")
        #     video.caption = caption
        #     video.likes = likes
        #     video.url = f"https://www.tiktok.com/@{kol.uniqueId}/video/{video_div.get('data-video-id')}"
        #     videos.append(video)
        #
        # kol.videos = videos
        self.result.append(kol)
        Log.info(f"Success: {url}")


# EOF
