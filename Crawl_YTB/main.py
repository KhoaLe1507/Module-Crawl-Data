import time
import logging
from ytb_data_utils import extract_channel_id, get_channel_info
from save_utils import append_to_json
from google.cloud import secretmanager
import json
import os
from flask import Flask, jsonify 

app = Flask(__name__)

# Thiết lập cấu hình logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
# Hàm chính của Cloud Function
def crawl_data(request):
    """Hàm được gọi bởi Cloud Functions để crawl và upload dữ liệu lên GCS."""
    
    INPUT_FILE = "urls.txt"
    
    try:
        # Đọc danh sách URL kênh từ file
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            channel_links = [line.strip() for line in f if line.strip()]
        
        all_channels = []

        # Chạy lấy thông tin kênh
        for links in channel_links:
            logging.info(f"Đang xử lý: {links}")
            channel_id = extract_channel_id(links)
            if not channel_id:
                logging.warning(f"Không tìm được channel ID từ {links}")
                continue

            channel_info = get_channel_info(channel_id)
            if not channel_info:
                logging.warning(f"Không lấy được thông tin cho kênh {channel_id}")
                continue

            all_channels.append(channel_info)

        # Upload file JSON lên GCS
        if all_channels:
            append_to_json("YTB_channels120.json", all_channels, "influencer-profile")
            logging.info("Dữ liệu đã được upload lên Google Cloud Storage thành công!")

        return jsonify({"message": "Dữ liệu đã được xử lý thành công!"}), 200

    except Exception as e:
        logging.error(f"Lỗi trong quá trình crawl: {e}")
        return jsonify({"error": str(e)}), 500

# Không cần gọi app.run() khi deploy lên Cloud Functions
