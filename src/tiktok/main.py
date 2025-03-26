from src.tiktok.scraper import TiktokScraper, TiktokConfig
from src.utils.log import Log


def scrape_tiktok():
    Log.start("Tiktok scraping started.")
    scraper = None
    try:
        config = TiktokConfig()
        scraper = TiktokScraper(config)
        scraper.run()
        Log.finish("Tiktok scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
