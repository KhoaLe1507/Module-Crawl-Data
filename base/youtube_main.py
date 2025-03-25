from youtube_scraper import YoutubeScraper, YoutubeConfig
from web_scraper import get_lines

if __name__ == "__main__":
    scraper = None

    try:
        config = YoutubeConfig()
        config.api_keys = get_lines("base/youtube_api_keys.txt")
        scraper = YoutubeScraper(config)
        urls = get_lines("base/youtube_urls.txt")
        scraper.run(urls)
        scraper.export("base/youtube_result.json")
        print("Scraper finished successfully.")
    finally:
        if scraper:
            scraper.close()

# EOF
