from typing import List
from src.scraper.web_scraper import ScrapeConfig
from src.scraper.result import ScrapeResult


class YoutubeConfig(ScrapeConfig):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "youtube"
        self.data_type = "channel"
        self.api_keys: List[str] = []


class YoutubeVideoComment(ScrapeResult):
    def __init__(self) -> None:
        self.channel_title: str | None = None
        self.video_id: int | None = None
        self.author: str | None = None
        self.text: str | None = None
        self.likeCount: int | None = None
        self.publishedAt: str | None = None
        super().__init__()


class YoutubeVideo(ScrapeResult):
    def __init__(self) -> None:
        self.video_id: str | None = None
        self.channel_title: str | None = None
        self.title: str | None = None
        self.publishedAt: str | None = None
        self.description: str | None = None
        self.tags: str | None = None
        self.duration: str | None = None
        self.definition: str | None = None
        self.viewCount: str | None = None
        self.likeCount: str | None = None
        self.commentCount: str | None = None
        self.privacyStatus: str | None = None
        self.embedHtml: str | None = None
        self.topics: list[str] | None = None
        self.liveViewers: str | None = None
        self.location: str | None = None
        self.madeForKids: bool | None = None
        super().__init__()


class YoutubeChannel(ScrapeResult):
    def __init__(self) -> None:
        self.channel_id: str | None = None
        self.channel_title: str | None = None
        self.description: str | None = None
        self.publishedAt: str | None = None
        self.customUrl: str | None = None
        self.country: str | None = None
        self.viewCount: str | None = None
        self.subscriberCount: str | None = None
        self.videoCount: str | None = None
        self.bannerUrl: str | None = None
        self.highThumbnail_Avatar: str | None = None
        self.keywords: str | None = None
        self.topics: list[str] | None = None
        self.communityGuidelinesGoodStanding: bool | None = None
        self.contentIdClaimsGoodStanding: bool | None = None
        self.copyrightStrikesGoodStanding: bool | None = None
        self.moderateComments: bool | None = None
        self.showRelatedChannels: bool | None = None
        self.moderationStatus: bool | None = None
        super().__init__()
        self.rename_dict["highThumbnail_Avatar"] = "highThumbnail/Avatar"


# EOF
