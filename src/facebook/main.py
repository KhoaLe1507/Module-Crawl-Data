from src.facebook.scraper import FacebookScraper, FacebookConfig
from src.utils.config import Config
from src.utils.log import Log
import json


def scrape_facebook():
    Log.start("Facebook scraping started.")
    scraper = None
    try:
        # Tạo file secret.json tại thư mục chính của repo
        config = FacebookConfig()
        if not Config.export_to_gcs:
            with open(
                f"{Config.secret_folder}/secret.json", "r", encoding="utf-8"
            ) as f:
                secret_info = json.load(f)

            config.username = secret_info["username"]
            config.password = secret_info["password"]
        scraper = FacebookScraper(config)
        scraper.run()
        Log.finish("Facebook scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
