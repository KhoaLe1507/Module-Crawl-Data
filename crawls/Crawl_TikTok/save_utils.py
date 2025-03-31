from google.cloud import storage
import pytz
from datetime import datetime,timezone
import time


def upload_to_gcs(bucket_name, file_path):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vn_tz)
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = int(time.time())  # Timestamp hiện tại (tính bằng giây)

        blob_name = f"tiktok/year={year}/month={month}/day={day}/tiktok_user_info_{timestamp}.json"

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)

        print(f"Đã upload {file_path} lên gs://{bucket_name}/{blob_name} thành công.")
        return f"gs://{bucket_name}/{blob_name}"

    except Exception as e:
        print(f"Lỗi khi upload GCS: {str(e)}")
        raise  # hoặc return lỗi tùy chiến lược
