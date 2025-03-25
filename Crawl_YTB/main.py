import time
from ytb_data_utils import extract_channel_id, get_channel_info
from save_utils import append_to_json
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="E:\Service_KEY\creator-dev-453406-5346d229c216.json"


if __name__ == "__main__":
    INPUT_FILE = "urls.txt"
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        channel_links = [line.strip() for line in f if line.strip()]

    all_channels = []

    for links in channel_links[0:1]:
        print(f"Đang xử lý: {links}")
        channel_id = extract_channel_id(links)
        if not channel_id:
            print(f" Không tìm được channel ID từ {links}")
            continue

        channel_info = get_channel_info(channel_id)
        if not channel_info:
            print(f" Không lấy được thông tin cho kênh {channel_id}")
            continue

        all_channels.append(channel_info)
    """
    Tam thoi chua can thiet lay thong tin cac video va comment !!!
        video_ids = get_latest_video_ids(channel_info["uploads_playlist_id"])
        videos = get_video_details(video_ids, channel_info["channel_title"])
        all_videos.extend(videos)

        for vid in video_ids:
            comments = get_video_comments(vid, channel_info["channel_title"])
            all_comments.extend(comments)
            time.sleep(0.2)
            
    """

    append_to_json("YTB_channels120.json", all_channels , "influencer-profile" )

    """
    Tam thoi chua can thiet lay thong tin cac video va comment !!!
    append_to_json("YTB_videos120.json", all_videos) 
    append_to_json("YTB_comments120.json", all_comments)
    """

    print("\n HOÀN TẤT! Dữ liệu đã được cập nhật.")
