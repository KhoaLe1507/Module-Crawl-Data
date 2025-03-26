from src.instagram.scraper import InstagramScraper
from src.instagram.config import InstagramConfig
from src.utils.log import Log


def scrape_instagram():
    Log.start("Instagram scraping started.")
    scraper = None

    try:
        config = InstagramConfig()
        scraper = InstagramScraper(config)
        scraper.run()
        Log.finish("Instagram scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
