from get_profile_data import get_profile_data
from save_utils import upload_to_gcs
import os

def crawl_tiktok(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return 'Authorization header missing', 403

        token = auth_header.split(" ")[1] if " " in auth_header else ""
        if not token:
            return 'Invalid token', 403

        get_profile_data()

        file_path = os.path.abspath("profile_data.json")
        if not os.path.exists(file_path):
            return 'Data file not found', 500

        upload_to_gcs("influencer-profile", file_path)
        return 'Profile data crawled and uploaded successfully.', 200

    except Exception as e:
        print(f"Lỗi trong crawl_tiktok: {str(e)}")
        return f'Lỗi hệ thống: {str(e)}', 500

