from rich import print

from manager import ScrapingManager
from data import read_urls, save_data
from config import *

if __name__ == '__main__':
    URLs = read_urls(TOP100_URLS_FILEPATH)

    print(f"[green]Number of urls: {len(URLs)}[/green]")

    scraping_manager = ScrapingManager(
        chrome_options=OPTIONS,
        experiment_options=EXPERIMENT_OPTIONS,
        num_workers=NUM_WORKERS,
        num_exception_workers=NUM_EXCEPTIONAL_WORKERS,
        logging_file=LOGGING_FILE
    )

    scraping_manager.start_drivers()
    scraping_manager.start_exceptional_drivers()

    data = scraping_manager.scrape(
        URLs,
        is_scraping_general_info=IS_SCRAPING_GENERAL_INFO,
        is_scraping_about_tab=IS_SCRAPING_ABOUT_TAB
    )

    save_data(data, TOP100_SAVING_FILEPATH)
