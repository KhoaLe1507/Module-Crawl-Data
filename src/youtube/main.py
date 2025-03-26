from src.youtube.scraper import YoutubeScraper, YoutubeConfig
from src.scraper.web_scraper import get_lines
from src.utils.log import Log
from src.utils.config import Config


def scrape_youtube():
    Log.start("Youtube scraping finished.")
    scraper = None
    try:
        config = YoutubeConfig()
        if not Config.export_to_gcs:
            config.api_keys = get_lines(f"{Config.secret_folder}/youtube_api_keys.txt")
        scraper = YoutubeScraper(config)
        scraper.run()
        Log.finish("Youtube scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
