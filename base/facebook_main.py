from facebook_scraper import FacebookScraper, FacebookConfig
from web_scraper import get_lines, export_json
import json

if __name__ == "__main__":
    scraper = None
    try:
        # Tạo file secret.json tại thư mục chính của repo
        with open("secret.json", "r", encoding="utf-8") as f:
            secret_info = json.load(f)

        username = secret_info["username"]
        password = secret_info["password"]
        config = FacebookConfig(username=username, password=password)
        scraper = FacebookScraper(config)
        urls = get_lines("base/facebook_urls.txt")
        scraper.run(urls)
        export_json(scraper.result, "base/facebook_result.json")
        print("Scraper finished successfully.")
    finally:
        if scraper:
            scraper.close()

# EOF
