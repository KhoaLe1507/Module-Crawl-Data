import os
import json
import traceback
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from apify_client import ApifyClient
from flask import jsonify, make_response, has_request_context
from core.apify_keys import API_KEYS
from core.key_manager import APIKeyManager
from google.cloud import storage
from datetime import datetime
import pytz

def upload_json_to_gcs(bucket_name, data):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(now.timestamp())

    blob_name = f"instagram/year={year}/month={month}/day={day}/instagram_user_infor_{timestamp}.json"
    blob = bucket.blob(blob_name)

    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    blob.upload_from_string(json_str, content_type="application/json")

    print(f"Đã upload dữ liệu JSON lên gs://{bucket_name}/{blob_name} thành công.")

def batched(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def process_batch(batch, results_limit, key_manager):
    """Cào dữ liệu cho 1 batch, thử nhiều key nếu gặp lỗi"""
    run_input = {
        "username": batch,
        "resultsLimit": results_limit,
    }

    for _ in range(len(API_KEYS)):
        api_key = key_manager.get()
        print(f"[Batch {batch}] Đang dùng API key: {api_key}")
        try:
            client = ApifyClient(api_key)
            run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise Exception("Không tìm thấy dataset ID")

            items = list(client.dataset(dataset_id).iterate_items())
            print(f"[Batch {batch}]Thành công với key {api_key}. Số lượng item: {len(items)}")
            return items
        except Exception as e:
            print(f"[Batch {batch}] Lỗi với key {api_key}: {e}")
            traceback.print_exc()
            key_manager.switch()

    print(f"[Batch {batch}] Tất cả key đều lỗi, bỏ qua batch này.")
    return []


def scrape_posts_from_usernames(usernames, results_limit, batch_size=2):
    batches = list(batched(usernames, batch_size=batch_size))
    key_managers = [APIKeyManager([API_KEYS[i % len(API_KEYS)]]) for i in range(len(batches))]

    results_dict = {}

    with ThreadPoolExecutor(max_workers=min(len(API_KEYS), len(batches))) as executor:
        future_to_index = {
            executor.submit(process_batch, batch, results_limit, key_managers[i]): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                items = future.result()
                results_dict[i] = items
            except Exception as exc:
                print(f"[Batch {i}] Gặp lỗi không mong muốn: {exc}")
                traceback.print_exc()

    all_items = []
    for i in sorted(results_dict.keys()):
        all_items.extend(results_dict[i])

    return all_items



def crawl_instagram_posts(request=None):
    try:
        request_json = request.get_json(silent=True)

        if not request_json or 'urls' not in request_json:
            return 'Missing "urls" in request body', 400

        urls = request_json['urls']
        if not isinstance(urls, list) or not all(isinstance(link, str) for link in urls):
            return '"urls" must be a list of strings', 400
        try:
            results_limit = int(request_json.get('NumberPost', 10))
        except ValueError:
            return '"NumberPost" must be an integer', 400

        print(f"Bắt đầu cào dữ liệu cho {len(urls)} user, mỗi user {results_limit} post")

        usernames = [url.rstrip("/").split("/")[-1] for url in urls]
        data = scrape_posts_from_usernames(usernames, results_limit, batch_size=2)

        upload_json_to_gcs("influencer-post", data)

        success_msg = f"Đã cào xong. Mỗi user: {results_limit} post."
        print(success_msg)
        return success_msg, 200

    except Exception as e:
        error_msg = f"Lỗi khi xử lý request: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, 500
