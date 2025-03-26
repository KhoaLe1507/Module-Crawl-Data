from src.facebook.main import scrape_facebook
from src.instagram.main import scrape_instagram
from src.tiktok.main import scrape_tiktok
from src.youtube.main import scrape_youtube
from log import Log

import time


def main():
    inp_folder = "input"
    out_folder = "output"
    starttime = time.time()
    scrape_facebook(inp_folder, out_folder)
    scrape_instagram(inp_folder, out_folder)
    scrape_tiktok(inp_folder, out_folder)
    scrape_youtube(inp_folder, out_folder)
    endtime = time.time()
    Log.info(f"Total time taken: {endtime - starttime}")


if __name__ == "__main__":
    main()
