# === File: api_keys.py ===
import requests
from google.cloud import secretmanager
import os

# Khởi tạo client Secret Manager
client = secretmanager.SecretManagerServiceClient()

# Đặt tên Secret và phiên bản bạn muốn truy xuất
project_id = 'creator-dev-453406'
secret_name = 'my-api-keys'
secret_version = 'latest'
secret_path = f'projects/{project_id}/secrets/{secret_name}/versions/{secret_version}'

def get_api_keys():
    try:
        response = client.access_secret_version(name=secret_path)
        api_keys_str = response.payload.data.decode("UTF-8")
        print(f"[DEBUG] Raw API Key string: [{api_keys_str}]")  # In luôn trong dấu [] để thấy rõ nếu rỗng
        api_keys = api_keys_str.splitlines()
        print(f"[DEBUG] Số lượng API key nạp được: {len(api_keys)}")
        return api_keys
    except Exception as e:
        print(f"[ERROR] Không thể truy xuất Secret: {e}")
        return []
# Đọc API keys từ Secret Manager
API_KEYS = get_api_keys()

current_key_index = 0

def get_api_key():
    global current_key_index
    if not API_KEYS:
        raise Exception("Không có API Key nào được tải từ Secret Manager!")
    return API_KEYS[current_key_index]

def rotate_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"Đang chuyển sang API Key thứ {current_key_index + 1}")


def safe_request(url):
    from api_keys import get_api_key, rotate_api_key, API_KEYS
    for _ in range(len(API_KEYS)):
        response = requests.get(url)
        data = response.json()
        if "error" in data:
            if data["error"].get("code") == 403:
                print("Hết quota cho API Key hiện tại. Thử key tiếp theo...")
                rotate_api_key()
                key = get_api_key()
                url = url.split("key=")[0] + f"key={key}"
                continue
            else:
                print("Lỗi khác từ API:", data["error"].get("message"))
                return None
        return data
    print("Đã thử hết API Keys nhưng vẫn lỗi.Đợi lúc 14h để được reset")
    return None