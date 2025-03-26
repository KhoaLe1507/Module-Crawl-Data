from facebook_main import scrape_facebook
from ins_main import scrape_instagram
from tiktok_main import scrape_tiktok
from youtube_main import scrape_youtube
from log import Log

import time


def main():
    inp_folder = "base/input"
    out_folder = "base/output"
    starttime = time.time()
    scrape_facebook(inp_folder, out_folder)
    scrape_instagram(inp_folder, out_folder)
    scrape_tiktok(inp_folder, out_folder)
    scrape_youtube(inp_folder, out_folder)
    endtime = time.time()
    Log.info(f"Total time taken: {endtime - starttime}")


if __name__ == "__main__":
    main()
