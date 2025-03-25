from log import Log

import urllib.parse
import requests
import regex


def get_channel_id_from_custom_url(url) -> str | None:
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

        Log.info(f"Không tìm thấy channelId trong HTML từ {decoded_url}")
        return None

    except Exception as e:
        Log.error(f"Lỗi khi truy cập {decoded_url}: {e}")
        return None


def extract_channel_id(url: str) -> str | None:
    url = str(url).strip()
    if "/channel/" in url:
        return url.split("/channel/")[-1].split("/")[0]
    elif "@" in url or "/c/" in url:
        return get_channel_id_from_custom_url(url)
    return None


# EOF
