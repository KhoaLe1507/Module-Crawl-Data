from src.youtube.scraper import YoutubeScraper, YoutubeConfig
from src.scraper.web_scraper import get_lines
from src.utils.log import Log
from src.utils.config import Config
from src.gcs.secret import GcsSecret


def scrape_youtube(gcs_secret: GcsSecret | None):
    Log.start("Youtube scraping finished.")
    scraper = None
    try:
        config = YoutubeConfig()
        if gcs_secret is None:
            config.api_keys = get_lines(f"{Config.secret_folder}/youtube_api_keys.txt")

        else:
            config.api_keys = gcs_secret.get_secret_list("my-api-keys")
        scraper = YoutubeScraper(config)
        scraper.run()
        Log.finish("Youtube scraping finished.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
