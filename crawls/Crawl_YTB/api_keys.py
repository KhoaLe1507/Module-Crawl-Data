# === File: api_keys.py ===
import requests

with open("api_keys.txt", "r") as f:
    API_KEYS = [line.strip() for line in f if line.strip()]
current_key_index = 0

def get_api_key():
    global current_key_index
    return API_KEYS[current_key_index]

def rotate_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f" Đang chuyển sang API Key thứ {current_key_index + 1}")

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