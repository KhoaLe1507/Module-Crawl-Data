from ins_scraper import InstagramScraper
from web_scraper import get_lines
from ins_config import InstagramConfig

if __name__ == "__main__":
    scraper = None

    try:
        urls = get_lines("base/ins_urls.txt")
        config = InstagramConfig()
        scraper = InstagramScraper(config)
        scraper.run(urls)
        scraper.export("base/ins_result.json")
        print("Scraper finished successfully.")
    finally:
        if scraper:
            scraper.close()

# EOF
