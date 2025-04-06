import os
import json
from apify_client import ApifyClient
from google.cloud import storage
from datetime import datetime
import pytz

APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

def upload_json_to_gcs(bucket_name, data):
    """
    Upload dữ liệu JSON trực tiếp lên GCS theo định dạng:
    instagram/year=yyyy/month=mm/day=dd/instagram_post_data_{timestamp}.json
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(now.timestamp())

    blob_name = f"instagram/year={year}/month={month}/day={day}/instagram_post_data_{timestamp}.json"
    blob = bucket.blob(blob_name)

    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    blob.upload_from_string(json_str, content_type="application/json")

    print(f"Đã upload dữ liệu JSON lên gs://{bucket_name}/{blob_name} thành công.")
    return f"gs://{bucket_name}/{blob_name}"

def scrape_posts(urls_file_path, results_limit=1):
    client = ApifyClient("APIFY_API_TOKEN")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(urls_file_path):
        urls_file_path = os.path.join(current_dir, urls_file_path)
    
    with open(urls_file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    usernames = [url.rstrip("/").split("/")[-1] for url in urls]
    
    run_input = {
        "username": usernames,
        "resultsLimit": results_limit,
    }

    run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)
    dataset_id = run.get("defaultDatasetId")

    if not dataset_id:
        print("Không tìm thấy dataset ID trong kết quả chạy Actor.")
        return

    print("Check your data here: https://console.apify.com/storage/datasets/" + dataset_id)

    items = list(client.dataset(dataset_id).iterate_items())
    items = sorted(items, key=lambda item: usernames.index(item["username"]) if "username" in item and item["username"] in usernames else len(usernames))

    gcs_path = upload_json_to_gcs("influencer-profile", items)
    print(f"Đường dẫn GCS: {gcs_path}")
