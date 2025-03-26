from google.cloud import storage
from datetime import datetime, timezone
import time
from src.utils.log import Log


def upload_to_gcs(bucket_name, file_path, platform, data_type):
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
    blob_name = f"{platform}/year={year}/month={month}/day={day}/{platform}_{data_type}_{timestamp}.json"

    # Tạo blob và upload
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

    Log.finish(f"Đã upload {file_path} lên gs://{bucket_name}/{blob_name} thành công.")
    return f"gs://{bucket_name}/{blob_name}"


# EOF
