from src.youtube.scraper import YoutubeScraper, YoutubeConfig
from web_scraper import get_lines, get_output_filename
from log import Log


def scrape_youtube(inp_folder: str, out_folder: str):
    Log.start("Youtube scraping finished.")
    scraper = None
    try:
        config = YoutubeConfig()
        config.api_keys = get_lines("base/youtube_api_keys.txt")
        scraper = YoutubeScraper(config)
        urls = get_lines(f"{inp_folder}/youtube_urls.txt")
        scraper.run(urls)
        output_filename = f"{out_folder}/{get_output_filename('youtube', 'channel')}"
        scraper.export(output_filename)
        Log.finish(f"Youtube scraping finished, exported to{output_filename}.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
