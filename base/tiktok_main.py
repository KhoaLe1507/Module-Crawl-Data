from tiktok_scraper import TiktokScraper, TiktokConfig
from web_scraper import get_lines
import json

if __name__ == "__main__":
    scraper = None
    try:
        # Tạo file secret.json tại thư mục chính của repo
        with open("secret.json", "r", encoding="utf-8") as f:
            secret_info = json.load(f)

        config = TiktokConfig()
        config.check()
        scraper = TiktokScraper(config)
        urls = get_lines("base/tiktok_urls.txt")
        scraper.run(urls)
        scraper.export("base/tiktok_result.json")
        print("Scraper finished successfully.")
    finally:
        if scraper:
            scraper.close()

# EOF
