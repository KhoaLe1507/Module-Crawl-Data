# === File: ytb_data_utils.py ===
import re
import urllib.parse
import requests
from api_keys import get_api_key, safe_request

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(decoded_url, headers=headers, timeout=10)
        html = response.text

        match = re.search(r'"channelId":"(UC[\w-]{22})"', html)
        if match:
            return match.group(1)

        match_alt = re.search(r'channel/UC[\w-]{22}', html)
        if match_alt:
            return match_alt.group(0).split("/")[-1]

        print(f"Không tìm thấy channelId trong HTML từ {decoded_url}")
        return None

    except Exception as e:
        print(f"Lỗi khi truy cập {decoded_url}: {e}")
        return None
#Đã bổ sung thêm các trường dữ liệu mới như topics,...
def get_channel_info(channel_id):
    api_key = get_api_key()
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,brandingSettings,contentDetails,topicDetails,localizations&id={channel_id}&key={api_key}"

    res = safe_request(url)
    if not res or not res.get("items"):
        return None
    data = res["items"][0]
    uploads_playlist_id = data["contentDetails"]["relatedPlaylists"]["uploads"]
    return {
        "channel_id": channel_id,
        "channel_title": data["snippet"]["title"],
        "description": data["snippet"].get("description", ""),
        "publishedAt": data["snippet"].get("publishedAt", ""),
        "customUrl": data["snippet"].get("customUrl", ""),
        "country": data["snippet"].get("country", "N/A"),
        "viewCount": data["statistics"].get("viewCount"),
        "subscriberCount": data["statistics"].get("subscriberCount", "hidden"),
        "videoCount": data["statistics"].get("videoCount"),
        "bannerUrl": data["brandingSettings"].get("image", {}).get("bannerExternalUrl", ""),
        "highThumbnail/Avatar": data["snippet"].get("thumbnails", {}).get("high", {}).get("url", ""),
        "keywords": data["brandingSettings"]["channel"].get("keywords", ""),
        "topics": [url.split("/")[-1] for url in data.get("topicDetails", {}).get("topicCategories", [])],
        "communityGuidelinesGoodStanding": data.get("auditDetails", {}).get("communityGuidelinesGoodStanding", False), # Kênh có vi phạm chính sách cộng đồng không
        "contentIdClaimsGoodStanding": data.get("auditDetails", {}).get("contentIdClaimsGoodStanding", False), # Trạng thái yêu cầu bản quyền nội dung
        "copyrightStrikesGoodStanding": data.get("auditDetails", {}).get("copyrightStrikesGoodStanding", False), # Trạng thái bản quyền có vi phạm không
        "moderateComments": data["brandingSettings"]["channel"].get("moderateComments", False),
        "showRelatedChannels": data["brandingSettings"]["channel"].get("showRelatedChannels", True),
        "moderationStatus": data.get("brandingSettings", {}).get("channel", {}).get("moderateComments", False)
    }

def get_latest_video_ids(playlist_id, max_results=10):
    api_key = get_api_key()
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults={max_results}&key={api_key}"
    res = safe_request(url)
    if not res or "items" not in res:
        print(f"Không lấy được video từ playlist {playlist_id}")
        return []
    return [item["snippet"]["resourceId"]["videoId"] for item in res["items"]]

def get_video_details(video_ids, channel_title):
    api_key = get_api_key()
    ids = ",".join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails,status,player,topicDetails,liveStreamingDetails,recordingDetails&id={ids}&key={api_key}"
    res = safe_request(url)
    videos = []
    for item in res.get("items", []):
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})
        status = item.get("status", {})
        if "duration" not in content:
            continue
        video = {
            "video_id": item["id"],
            "channel_title": channel_title,
            "title": snippet.get("title", ""),
            "publishedAt": snippet.get("publishedAt", ""),
            "description": snippet.get("description", ""),
            "tags": ", ".join(snippet.get("tags", [])),
            "duration": content.get("duration", ""),
            "definition": content.get("definition", ""),
            "viewCount": stats.get("viewCount", 0),
            "likeCount": stats.get("likeCount", 0),
            "commentCount": stats.get("commentCount", 0),
            "privacyStatus": status.get("privacyStatus", ""),
            "embedHtml": item.get("player", {}).get("embedHtml", ""),
            "topics": item.get("topicDetails", {}).get("relevantTopicIds", []),
            "liveViewers": item.get("liveStreamingDetails", {}).get("concurrentViewers", ""),
            "location": item.get("recordingDetails", {}).get("locationDescription", ""),
            "madeForKids": status.get("madeForKids", False)
        }
        videos.append(video)
    return videos

def get_video_comments(video_id, channel_title, max_results=30):
    api_key = get_api_key()
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults={max_results}&key={api_key}"
    res = safe_request(url)
    comments = []
    for item in res.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "channel_title": channel_title,
            "video_id": video_id,
            "author": snippet.get("authorDisplayName", ""),
            "text": snippet.get("textDisplay", ""),
            "likeCount": snippet.get("likeCount", 0),
            "publishedAt": snippet.get("publishedAt", "")
        })
    return comments