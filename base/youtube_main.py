from youtube_scraper import YoutubeScraper, YoutubeConfig
from web_scraper import get_lines, export_json

if __name__ == "__main__":
    scraper = None

    try:
        with open("base/youtube_api_keys.txt", "r", encoding="utf-8") as f:
            api_keys = [line.strip() for line in f.readlines() if line.strip()]

        config = YoutubeConfig()
        config.api_keys = api_keys
        scraper = YoutubeScraper(config)
        urls = get_lines("base/youtube_urls.txt")
        scraper.run(urls)
        export_json(scraper.result, "base/youtube_result.json")
        print("Scraper finished successfully.")
    finally:
        if scraper:
            scraper.close()

# EOF
