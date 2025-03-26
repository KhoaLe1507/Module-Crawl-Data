import os
import time
import random
import json
from scrapers import scrape_user_fallback, parse_user, save_to_file

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(current_dir, "instagram_data.json")
    input_file = os.path.join(current_dir, "urls.txt")

    # Ghi đè file output cũ khi chương trình bắt đầu (khởi tạo thành danh sách rỗng)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print("Đã khởi tạo file output thành công.")
    except Exception as e:
        print(f"Lỗi khi khởi tạo file output: {e}")
        return

    # Đọc danh sách URL từ file input
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            urls = f.readlines()
    except Exception as e:
        print(f"Lỗi khi đọc file input: {e}")
        return

    # Trích xuất username từ URL
    usernames = [url.strip().rstrip("/").split("/")[-1] for url in urls]

    for username in usernames:
        try:
            # Thực hiện cào dữ liệu
            user_data = scrape_user_fallback(username)
            parsed_data = parse_user(user_data)
            save_to_file(output_file, parsed_data)
            print(f"Đã lưu dữ liệu cho: {username}")
            delay = random.uniform(20, 30)
            print(f"Delay: {delay:.2f} giây")
            time.sleep(delay)
        except Exception as e:
            # Khi gặp lỗi (ví dụ bị chặn) thì in lỗi và dừng chương trình
            print(f"Lỗi khi cào dữ liệu của {username}: {e}")
            print("Dừng chương trình do lỗi.")
            break

if __name__ == '__main__':
    main()
