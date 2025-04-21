import os
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from apify_client import ApifyClient
from core.apify_keys import API_KEYS
from core.key_manager import APIKeyManager
import time
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
    return f"gs://{bucket_name}/{blob_name}"


def batched(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def process_batch(batch, key_manager):
    """Thử nhiều API key để xử lý 1 batch. Nếu tất cả fail thì trả về []"""
    run_input = {"usernames": batch}

    for _ in range(len(API_KEYS)):
        api_key = key_manager.get()
        print(f"[Batch {batch}] Dùng API key: {api_key}")
        try:
            client = ApifyClient(api_key)
            run = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise Exception("Không tìm thấy dataset ID")

            items = list(client.dataset(dataset_id).iterate_items())

            for item in items:
                item.pop("relatedProfiles", None)
                if "latestPosts" in item and isinstance(item["latestPosts"], list):
                    for post in item["latestPosts"]:
                        post.pop("childPosts", None)

            # Giữ đúng thứ tự usernames trong batch
            items = sorted(items, key=lambda item: batch.index(item["username"]) if "username" in item else len(batch))

            print(f"[Batch {batch}] Thành công với {len(items)} user")
            return items

        except Exception as e:
            print(f"[Batch {batch}] Lỗi với key {api_key}: {e}")
            traceback.print_exc()
            key_manager.switch()

    print(f"[Batch {batch}] Tất cả key đều lỗi. Bỏ qua.")
    return []


def scrape_profiles_from_usernames(usernames, batch_size=2):
    batches = list(batched(usernames, batch_size=batch_size))
    key_managers = [APIKeyManager([API_KEYS[i % len(API_KEYS)]]) for i in range(len(batches))]

    results_dict = {}

    with ThreadPoolExecutor(max_workers=min(len(API_KEYS), len(batches))) as executor:
        future_to_index = {
            executor.submit(process_batch, batch, key_managers[i]): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                items = future.result()
                results_dict[i] = items
            except Exception as exc:
                print(f"[Batch {i}] Lỗi không mong muốn: {exc}")
                traceback.print_exc()

    all_items = []
    for i in sorted(results_dict.keys()):
        all_items.extend(results_dict[i])

    return all_items


def crawl_instagram_profiles(request):
    try:
        request_json = request.get_json(silent=True)

        if not request_json or "urls" not in request_json:
            return "Thiếu 'urls' trong request body", 400

        urls = request_json["urls"]
        if not isinstance(urls, list) or not all(isinstance(u, str) for u in urls):
            return "'urls' phải là danh sách chuỗi", 400

        try:
            batch_size = int(request_json.get("batch_size", 2))
        except ValueError:
            return "'batch_size' phải là số nguyên", 400

        print(f"Bắt đầu cào dữ liệu cho {len(urls)} user, batch size: {batch_size}")

        usernames = [url.rstrip("/").split("/")[-1] for url in urls]

        data = scrape_profiles_from_usernames(usernames, batch_size)

        gcs_path = upload_json_to_gcs("influencer-profile", data)

        msg = f"Hoàn tất. Đã upload JSON tới: {gcs_path}"
        print(msg)
        return msg, 200

    except Exception as e:
        err_msg = f"Lỗi khi xử lý: {str(e)}"
        print(err_msg)
        traceback.print_exc()
        return err_msg, 500




