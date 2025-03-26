from src.youtube.scraper import YoutubeScraper, YoutubeConfig
from src.scraper.web_scraper import get_lines
from src.utils.log import Log
from src.scraper.config import ScrapeConfig


def scrape_youtube():
    Log.start("Youtube scraping finished.")
    scraper = None
    try:
        config = YoutubeConfig()
        if not ScrapeConfig.export_to_gcs:
            config.api_keys = get_lines(
                f"{ScrapeConfig.secret_folder}/youtube_api_keys.txt"
            )
        scraper = YoutubeScraper(config)
        scraper.run()
        Log.finish("Youtube scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
