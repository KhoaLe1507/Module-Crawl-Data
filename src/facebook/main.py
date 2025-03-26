from src.facebook.scraper import FacebookScraper, FacebookConfig
from src.scraper.web_scraper import get_lines, get_output_filename
from src.utils.log import Log
import json


def scrape_facebook(inp_folder: str, out_folder: str):
    Log.start("Facebook scraping started.")
    scraper = None
    try:
        # Tạo file secret.json tại thư mục chính của repo
        with open(f"{inp_folder}/secrets/secret.json", "r", encoding="utf-8") as f:
            secret_info = json.load(f)

        config = FacebookConfig()
        config.username = secret_info["username"]
        config.password = secret_info["password"]
        config.check()
        scraper = FacebookScraper(config)
        urls = get_lines(f"{inp_folder}/facebook_urls.txt")
        scraper.run(urls)
        output_filename = f"{out_folder}/{get_output_filename('facebook', 'profile')}"
        scraper.export(output_filename)
        Log.finish(f"Facebook scraping finished, exported to {output_filename}.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
