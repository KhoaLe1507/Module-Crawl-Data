import os
import json
from apify_client import ApifyClient
from google.cloud import storage
from datetime import datetime
import pytz
import time

# Lấy APIFY_API_TOKEN từ biến môi trường
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

def upload_to_gcs(bucket_name, file_path):
    """
    Upload file lên GCS theo định dạng:
    instagram/year=yyyy/month=mm/day=dd/instagram_user_infor_{timestamp}.json
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(time.time())

    blob_name = f"instagram/year={year}/month={month}/day={day}/instagram_post_data_{timestamp}.json"

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    print(f"Đã upload {file_path} lên gs://{bucket_name}/{blob_name} thành công.")
    return f"gs://{bucket_name}/{blob_name}"

def scrape_posts(urls_file_path, output_file_path, results_limit=30):
    client = ApifyClient(APIFY_API_TOKEN)
    
    # Xác định đường dẫn tuyệt đối nếu cần
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(urls_file_path):
        urls_file_path = os.path.join(current_dir, urls_file_path)
    if not os.path.isabs(output_file_path):
        output_file_path = os.path.join(current_dir, output_file_path)
    
    # Đọc danh sách URL từ file
    with open(urls_file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Trích xuất tên người dùng từ URL
    usernames = [url.rstrip("/").split("/")[-1] for url in urls]
    
    # Chuẩn bị dữ liệu input cho Actor
    run_input = {
        "username": usernames,
        "resultsLimit": results_limit,
    }
    
    # Chạy Actor Instagram Post Scraper
    run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)
    
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        print("Không tìm thấy dataset ID trong kết quả chạy Actor.")
        return
    
    print("Check your data here: https://console.apify.com/storage/datasets/" + dataset_id)
    
    # Lấy dữ liệu từ dataset và lưu vào file JSON
    items = list(client.dataset(dataset_id).iterate_items())

    # Sắp xếp lại items theo thứ tự của usernames trong file urls
    items = sorted(items, key=lambda item: usernames.index(item["username"]) if "username" in item and item["username"] in usernames else len(usernames))
    
    # Lưu dữ liệu vào file JSON
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    
    print(f"Đã lưu dữ liệu vào {output_file_path}")

    # Upload dữ liệu lên GCS
    gcs_path = upload_to_gcs("influencer-profile", output_file_path)
    print(f"Đường dẫn GCS: {gcs_path}")
