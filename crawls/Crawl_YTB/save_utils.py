from google.cloud import storage
import os
from datetime import datetime,timezone
import time
import json

def append_to_json(filename, new_data ,namebucket):
    """Ghi dữ liệu vào file JSON, luôn tạo file mới"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print(f"Đã ghi {len(new_data)} dòng vào {filename}")
    file_path=os.path.abspath(filename)
    upload_to_gcs( namebucket , file_path)

def upload_to_gcs(bucket_name, file_path):
    """Upload file lên GCS theo định dạng YouTube/year=yyyy/month=mm/day=dd/YouTube_datatype_timestamp.json"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Lấy thời gian hiện tại
    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(time.time())  # Timestamp hiện tại (tính bằng giây)

    # Tạo blob_name theo format yêu cầu
    blob_name = f"youtube/year={year}/month={month}/day={day}/youtube_{"channel_info"}_{timestamp}.json"

    # Tạo blob và upload
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    print(f"Đã upload {file_path} lên gs://{bucket_name}/{blob_name} thành công.")
    return f"gs://{bucket_name}/{blob_name}"