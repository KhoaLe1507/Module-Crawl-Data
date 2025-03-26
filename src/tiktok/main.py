from src.tiktok.scraper import TiktokScraper, TiktokConfig
from web_scraper import get_lines, get_output_filename
from log import Log


def scrape_tiktok(inp_folder: str, out_folder: str):
    Log.start("Tiktok scraping started.")
    scraper = None
    try:
        config = TiktokConfig()
        config.check()
        scraper = TiktokScraper(config)
        urls = get_lines(f"{inp_folder}/tiktok_urls.txt")
        scraper.run(urls)
        output_filename = (
            f"{out_folder}/output/{get_output_filename('tiktok', 'profile')}"
        )
        scraper.export(output_filename)
        Log.finish(f"Tiktok scraping finished, exported to {output_filename}.")
    except Exception as e:
        Log.exception(e)
    finally:
        if scraper:
            scraper.close()


# EOF
