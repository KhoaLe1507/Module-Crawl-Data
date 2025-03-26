from ins_scraper import InstagramScraper
from ins_config import InstagramConfig
from web_scraper import get_lines, get_output_filename
from log import Log


def scrape_instagram(inp_folder: str, out_folder):
    Log.start("Instagram scraping started.")
    scraper = None

    try:
        config = InstagramConfig()
        scraper = InstagramScraper(config)
        urls = get_lines(f"{inp_folder}/instagram_urls.txt")
        scraper.run(urls)
        output_filename = f"{out_folder}/{get_output_filename('instagram', 'profile')}"
        scraper.export(output_filename)
        Log.finish(f"Instagram scraping finished, exported to {output_filename}.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
