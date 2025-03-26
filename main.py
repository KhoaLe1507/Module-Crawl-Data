from src.facebook.main import scrape_facebook
from src.instagram.main import scrape_instagram
from src.tiktok.main import scrape_tiktok
from src.youtube.main import scrape_youtube
from src.utils.log import Log

import time


def main():
    starttime = time.time()
    scrape_facebook()
    scrape_instagram()
    scrape_tiktok()
    scrape_youtube()
    endtime = time.time()
    Log.info(f"Total time taken: {endtime - starttime}")


if __name__ == "__main__":
    main()
