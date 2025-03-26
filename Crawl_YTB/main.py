import time
from ytb_data_utils import extract_channel_id, get_channel_info
from save_utils import append_to_json



# Hàm chính của Cloud Function
def crawl_youtube_channel(request):
    """Hàm xử lý yêu cầu HTTP từ Cloud Function"""
    # Kiểm tra Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return 'Authorization header missing', 403  # Nếu không có Authorization header, trả về lỗi 403

    # Lấy Bearer Token từ header
    token = auth_header.split(" ")[1] if " " in auth_header else ""
    
    if not token:
        return 'Invalid token', 403  # Nếu không có token, trả về lỗi

    # Tiếp theo xử lý URL kênh YouTube
    INPUT_FILE = "urls.txt"
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            channel_links = [line.strip() for line in f if line.strip()]
        
        all_channels = []

        for links in channel_links:
            print(f"Đang xử lý: {links}")
            channel_id = extract_channel_id(links)
            if not channel_id:
                print(f"Không tìm được channel ID từ {links}")
                continue

            channel_info = get_channel_info(channel_id)
            if not channel_info:
                print(f"Không lấy được thông tin cho kênh {channel_id}")
                continue

            all_channels.append(channel_info)

        # Upload file JSON lên GCS
        if all_channels:
            append_to_json("YTB_channels120.json", all_channels, "influencer-profile")
            print("Dữ liệu đã được upload lên Google Cloud Storage thành công!")

        return "Dữ liệu đã được xử lý thành công!"
    
    except Exception as e:
        print(f"Lỗi trong quá trình crawl: {e}")
        return f"Lỗi: {e}", 500
