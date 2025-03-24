import os
import json

def append_to_json(filename, new_data):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    old_ids = {item.get("channel_id") or item.get("video_id") for item in old_data}
    filtered = [item for item in new_data if (item.get("channel_id") or item.get("video_id")) not in old_ids]
    combined_data = old_data + filtered

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    print(f"Đã thêm {len(filtered)} dòng mới vào {filename}")
