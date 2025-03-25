# === File: api_keys.py ===
import requests

from google.cloud import secretmanager
import json

# Khởi tạo client để truy xuất Secret Manager
client = secretmanager.SecretManagerServiceClient()

# Đặt tên Secret và phiên bản bạn muốn truy xuất
project_id = 'creator-dev-453406'
secret_name = 'my-api-keys'
secret_version = 'latest'
secret_path = f'projects/{project_id}/secrets/{secret_name}/versions/{secret_version}'

# Lấy API keys từ Secret Manager
def get_api_keys():
    response = client.access_secret_version(name=secret_path)
    api_keys_str = response.payload.data.decode("UTF-8")
    
    # Giả sử API keys được lưu dưới dạng mỗi key 1 dòng, tương tự file api_keys.txt
    api_keys = api_keys_str.splitlines()
    return api_keys

# Đọc API key từ Secret Manager
API_KEYS = get_api_keys()
current_key_index = 0

def get_api_key():
    global current_key_index
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