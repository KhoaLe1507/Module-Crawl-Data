import json
from src.facebook.main import scrape_facebook
from src.instagram.main import scrape_instagram
from src.tiktok.main import scrape_tiktok
from src.youtube.main import scrape_youtube
from src.utils.log import Log
from src.utils.config import Config

import time


def load_configs():
    with open("config.json", "r") as f:
        configs = json.load(f)

    Config.set_configs(configs)


def main():
    load_configs()
    starttime = time.time()
    scrape_facebook()
    scrape_instagram()
    scrape_tiktok()
    scrape_youtube()
    endtime = time.time()
    Log.info(f"Total time taken: {endtime - starttime}")


if __name__ == "__main__":
    main()
