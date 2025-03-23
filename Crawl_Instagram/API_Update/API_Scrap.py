import json
import httpx
import jmespath
import os
import time
import random

client = httpx.Client(
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

def scrape_user(username: str):
    """Scrape Instagram user's data"""
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

def parse_user(data: dict) -> dict:
    """Parse Instagram user's web dataset for relevant data"""
    result = jmespath.search(
        """{
            name: full_name,
            username: username,
            id: id,
            category: category_name,
            email: business_email,
            mobile: business_phone_number,
            address: business_address_json,
            website: external_url,
            tiktok: bio_links[?contains(@.url, 'tiktok')].url,
            bio: biography,
            bio_links: bio_links[].url,
            homepage: external_url,
            followers: edge_followed_by.count,
            follows: edge_follow.count,
            facebook_id: fbid,
            is_private: is_private,
            is_verified: is_verified,
            profile_image: profile_pic_url_hd
        }""",
        data,
    )
    return result

def save_to_file(filename: str, data):
    """Append each user's data to the JSON file"""
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)  # Tạo file rỗng nếu chưa có

    with open(filename, "r", encoding="utf-8") as f:
        existing_data = json.load(f)  # Đọc dữ liệu hiện có

    existing_data.append(data)  # Thêm dữ liệu mới vào danh sách

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)  # Ghi lại toàn bộ file

# Lấy thư mục hiện tại của file .py đang chạy
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "instagram_API_Update.json")

# Đọc danh sách username từ file
file_input_path = "D:/DUT 2/HK2/Yeah1/API_Update/instagram.txt"
with open(file_input_path, "r") as f:
    urls = f.readlines()

usernames = [url.strip().rstrip("/").split("/")[-1] for url in urls]

# Cào dữ liệu từng user và lưu ngay vào file
for username in usernames:
    try:
        user_data = scrape_user(username)
        parsed_data = parse_user(user_data)
        save_to_file(file_path, parsed_data)  # Lưu ngay sau khi cào được
        print(f"✅ Đã lưu dữ liệu cho: {username}")

        # Tạo độ trễ ngẫu nhiên từ 3 đến 7 giây để tránh bị phát hiện là bot
        delay = random.uniform(20, 30)
        print(f"⏳ Chờ {delay:.2f} giây trước khi tiếp tục...")
        time.sleep(delay)
        
    except Exception as e:
        print(f"❌ Lỗi khi cào dữ liệu của {username}: {e}")
