from facebook_scraper import FacebookScraper
from web_scraper import get_lines, export_json

if __name__ == "__main__":
    scraper = FacebookScraper()
    try:
        urls = get_lines("urls.txt")
        scraper.run(urls)
        export_json(scraper.result, "result.json")
        print("Scraper finished successfully.")
    finally:
        scraper.close()
