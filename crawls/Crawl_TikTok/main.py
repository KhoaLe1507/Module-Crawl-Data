from crawls.Crawl_TikTok.get_profile_data import get_profile_data
import os

from crawls.Crawl_TikTok.save_utils import upload_to_gcs

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="C:\\SERVICE-key\\creator-dev-453406-ee12ad89e976.json"
if __name__ == '__main__':
    get_profile_data()
    file_path = os.path.abspath("profile_data.json")
    upload_to_gcs("influencer-profile", file_path)