import os
import json
import traceback
from datetime import datetime
import pytz
from flask import jsonify, make_response

from apify_client import ApifyClient
from google.cloud import storage

# Lấy token từ biến môi trường
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

def upload_json_to_gcs(bucket_name, data):
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
    client = ApifyClient(APIFY_API_TOKEN)

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

    gcs_path = upload_json_to_gcs("influencer-post", items)
    print(f"Đường dẫn GCS: {gcs_path}")

def crawl_instagram_posts(request):
    current_dir = os.path.dirname(__file__)
    urls_file = os.path.join(current_dir, "urls.txt")
    results_limit = 1

    if not os.path.exists(urls_file):
        print("Không tìm thấy file urls.txt")
        return make_response(jsonify({"error": "File urls.txt không tồn tại"}), 500)

    try:
        print("Bắt đầu cào dữ liệu post...")
        scrape_posts(urls_file, results_limit)
        print("Hoàn tất cào dữ liệu post.")
    except Exception as e:
        print("Lỗi khi cào dữ liệu post:", e)
        traceback.print_exc()
        return make_response(jsonify({
            "error": "Lỗi khi cào dữ liệu post",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500)

    response_data = {
        "message": "Dữ liệu đã được cào thành công từ Instagram",
    }

    return jsonify(response_data)
