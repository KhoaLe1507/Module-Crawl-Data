from typing import List, override
import requests
import urllib.parse
import regex
import logging

from web_scraper import Config, ScrapeResult, WebScraper


def extract_channel_id(url):
    url = str(url).strip()
    if "/channel/" in url:
        return url.split("/channel/")[-1].split("/")[0]
    elif "@" in url or "/c/" in url:
        return get_channel_id_from_custom_url(url)
    return None


def get_channel_id_from_custom_url(url):
    decoded_url = urllib.parse.unquote(url).strip()
    if not decoded_url.startswith("http"):
        decoded_url = "https://" + decoded_url

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(decoded_url, headers=headers, timeout=10)
        html = response.text

        match = regex.search(r'"channelId":"(UC[\w-]{22})"', html)
        if match:
            return match.group(1)

        match_alt = regex.search(r"channel/UC[\w-]{22}", html)
        if match_alt:
            return match_alt.group(0).split("/")[-1]

        logging.info(f"Không tìm thấy channelId trong HTML từ {decoded_url}")
        return None

    except Exception as e:
        logging.error(f"Lỗi khi truy cập {decoded_url}: {e}")
        return None


class YoutubeConfig(Config):
    def __init__(self) -> None:
        super().__init__()
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
        self.keywords: str | None = None
        self.topics: list[str] | None = None
        self.localizations: list[str] | None = None
        self.defaultLanguage: str | None = None
        self.featuredChannels: list[str] | None = None
        self.moderateComments: bool | None = None
        self.showRelatedChannels: bool | None = None
        self.uploads_playlist_id: str | None = None
        super().__init__()


class YoutubeScraper(WebScraper):
    def __init__(self, config: YoutubeConfig) -> None:
        super().__init__(config)
        self.config = config
        self.current_key_index = 0

    def get_api_key(self) -> str:
        return self.config.api_keys[self.current_key_index]

    def rotate_api_key(self) -> None:
        self.current_key_index = (self.current_key_index + 1) % len(
            self.config.api_keys
        )
        logging.info(f" Đang chuyển sang API Key thứ {self.current_key_index + 1}")

    def safe_request(self, url):
        for _ in range(len(self.config.api_keys)):
            response = requests.get(url)
            data = response.json()
            if "error" in data:
                if data["error"].get("code") == 403:
                    logging.info("Hết quota cho API Key hiện tại. Thử key tiếp theo...")
                    self.rotate_api_key()
                    key = self.get_api_key()
                    url = url.split("key=")[0] + f"key={key}"
                    continue
                else:
                    logging.error("Lỗi khác từ API:", data["error"].get("message"))
                    return
            return data
        logging.info("Đã thử hết API Keys nhưng vẫn lỗi.Đợi lúc 14h để được reset")
        return None

    @override
    def run(self, urls: list[str]) -> None:
        for url in urls:
            logging.info(f"Đang xử lý: {url}")
            channel_id = extract_channel_id(url)
            if not channel_id:
                logging.info(f" Không tìm được channel ID từ {url}")
                continue

            channel_info = self.get_channel_info(channel_id)
            if not channel_info:
                logging.info(f" Không lấy được thông tin cho kênh {channel_id}")
                continue

            self.result.append(channel_info)

    def get_channel_info(self, channel_id):
        api_key = self.get_api_key()
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,brandingSettings,contentDetails,topicDetails,localizations&id={channel_id}&key={api_key}"

        res = self.safe_request(url)
        if not res or not res.get("items"):
            return None
        data = res["items"][0]
        uploads_playlist_id = data["contentDetails"]["relatedPlaylists"]["uploads"]
        channel = YoutubeChannel()
        channel.channel_id = channel_id
        channel.channel_title = data["snippet"]["title"]
        channel.description = data["snippet"].get("description", "")
        channel.publishedAt = data["snippet"].get("publishedAt", "")
        channel.customUrl = data["snippet"].get("customUrl", "")
        channel.country = data["snippet"].get("country", "N/A")
        channel.viewCount = data["statistics"].get("viewCount")
        channel.subscriberCount = data["statistics"].get("subscriberCount", "hidden")
        channel.videoCount = data["statistics"].get("videoCount")
        channel.bannerUrl = (
            data["brandingSettings"].get("image", {}).get("bannerExternalUrl", "")
        )
        channel.keywords = data["brandingSettings"]["channel"].get(
            "keywords", ""
        )  # Config by user
        channel.topics = data.get("topicDetails", {}).get(
            "topicCategories", []
        )  # Config by YTB system
        channel.localizations = list(data.get("localizations", {}).keys())
        channel.defaultLanguage = data["brandingSettings"]["channel"].get(
            "defaultLanguage", ""
        )
        channel.featuredChannels = data["brandingSettings"]["channel"].get(
            "featuredChannelsUrls", []
        )
        channel.moderateComments = data["brandingSettings"]["channel"].get(
            "moderateComments", False
        )
        channel.showRelatedChannels = data["brandingSettings"]["channel"].get(
            "showRelatedChannels", True
        )
        channel.uploads_playlist_id = uploads_playlist_id
        return channel

    def get_latest_video_ids(self, playlist_id, max_results=10):
        api_key = self.get_api_key()
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={api_key}"
        res = self.safe_request(url)
        if not res or "items" not in res:
            logging.info(f"Không lấy được video từ playlist {playlist_id}")
            return []
        return [item["snippet"]["resourceId"]["videoId"] for item in res["items"]]

    def get_video_details(self, video_ids, channel_title) -> List[YoutubeVideo]:
        api_key = self.get_api_key()
        ids = ",".join(video_ids)
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,status,player,topicDetails,liveStreamingDetails,recordingDetails&id={ids}&key={api_key}"
        res = self.safe_request(url)
        videos = []
        if res is None:
            return videos
        for item in res.get("items", []):
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})
            status = item.get("status", {})
            if "duration" not in content:
                continue
            video = YoutubeVideo()
            video.video_id = item["id"]
            video.channel_title = channel_title
            video.title = snippet.get("title", "")
            video.publishedAt = snippet.get("publishedAt", "")
            video.description = snippet.get("description", "")
            video.tags = ", ".join(snippet.get("tags", []))
            video.duration = content.get("duration", "")
            video.definition = content.get("definition", "")
            video.viewCount = stats.get("viewCount", 0)
            video.likeCount = stats.get("likeCount", 0)
            video.commentCount = stats.get("commentCount", 0)
            video.privacyStatus = status.get("privacyStatus", "")
            video.embedHtml = item.get("player", {}).get("embedHtml", "")
            video.topics = item.get("topicDetails", {}).get("relevantTopicIds", [])
            video.liveViewers = item.get("liveStreamingDetails", {}).get(
                "concurrentViewers", ""
            )
            video.location = item.get("recordingDetails", {}).get(
                "locationDescription", ""
            )
            video.madeForKids = status.get("madeForKids", False)
            videos.append(video)
        return videos

    def get_video_comments(
        self, video_id, channel_title, max_results=30
    ) -> List[YoutubeVideoComment]:
        api_key = self.get_api_key()
        url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults={max_results}&key={api_key}"
        res = self.safe_request(url)
        comments = []
        if res is None:
            return comments
        for item in res.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comment = YoutubeVideoComment()
            comment.channel_title = channel_title
            comment.video_id = video_id
            comment.author = snippet.get("authorDisplayName", "")
            comment.text = snippet.get("textDisplay", "")
            comment.likeCount = snippet.get("likeCount", 0)
            comment.publishedAt = snippet.get("publishedAt", "")
            comments.append(comment)
        return comments


# EOF
