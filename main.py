import json

from src.facebook.main import scrape_facebook
from src.instagram.main import scrape_instagram
from src.tiktok.main import scrape_tiktok
from src.youtube.main import scrape_youtube
from src.utils.log import Log
from src.utils.config import Config
from src.gcs.secret import GcsSecret

import time
import os


def load_configs():
    with open("config.json", "r") as f:
        configs = json.load(f)

    Config.input_folder = configs["input_folder"]
    Config.output_folder = configs["output_folder"]
    Config.secret_folder = configs["secret_folder"]
    Config.bucket_name = configs["bucket_name"]
    Config.product_mode = configs["product_mode"]
    Config.project_id = configs["project_id"]


def head():
    load_configs()
    if Config.product_mode:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(
            f"{Config.secret_folder}/creator-dev-453406-dcbfdc47e0e1.json"
        )


def body():
    gcs_secret = None
    if Config.product_mode:
        gcs_secret = GcsSecret()
    starttime = time.time()
    if not Config.product_mode:
        scrape_facebook(gcs_secret)
    scrape_instagram()
    scrape_tiktok()
    scrape_youtube(gcs_secret)
    endtime = time.time()
    Log.info(f"Total time taken: {endtime - starttime}")


def gcs_main(request):
    head()
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return (
            "Authorization header missing",
            403,
        )  # Nếu không có Authorization header, trả về lỗi 403

    # Lấy Bearer Token từ header
    token = auth_header.split(" ")[1] if " " in auth_header else ""

    if not token:
        return "Invalid token", 403  # Nếu không có token, trả về lỗi

    body()


def main():
    head()
    body()


if __name__ == "__main__":
    main()

# EOF
