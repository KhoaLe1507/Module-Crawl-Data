import argparse
import getpass

from rich import print

from manager import ScrapingManager
from data import read_urls, save_data
from config import *

if __name__ == '__main__':
    # Create argparse
    parser = argparse.ArgumentParser(description="Main argparse")

    # Add arguments
    parser.add_argument('-i', '--inputfile', type=str, default=TOP100_URLS_FILEPATH, help="Url file")
    parser.add_argument('-s', '--savefile', type=str, default=TOP100_SAVING_FILEPATH, help="Saving file")
    parser.add_argument('-l', '--logfile', type=str, default=LOGGING_FILE, help="Logging file")
    parser.add_argument('-o', '--options', type=str, nargs="+", default=OPTIONS, help="Options")
    parser.add_argument('-eo', '--experiment-options', type=list, nargs="+",default=EXPERIMENT_OPTIONS, help="Experiment options")
    parser.add_argument('-nw', '--num_workers', type=int, default=NUM_WORKERS, help="Number of workers")
    parser.add_argument('-exw', '--num_exceptional_workers', type=int, default=NUM_EXCEPTIONAL_WORKERS, help="Number of exceptional workers")
    parser.add_argument('-isgi', '--is_scraping_general_info', type=bool, default=IS_SCRAPING_GENERAL_INFO, help="Is scraping general info")
    parser.add_argument('-isat', '--is_scraping_about_tab', type=bool, default=IS_SCRAPING_ABOUT_TAB, help='Is scraping about tab')
    parser.add_argument('-u', '--username', type=str, help='username')

    args = parser.parse_args()

    if not args.username:
        raise ValueError("Username must be provided")

    if args.username:
        args.password = getpass.getpass("Enter password: ")

    URLs = read_urls(args.inputfile)

    print(f"[green]Number of urls: {len(URLs)}[/green]")

    scraping_manager = ScrapingManager(
        chrome_options=args.options,
        experiment_options=args.experiment_options,
        num_workers=args.num_workers,
        num_exception_workers=args.num_exceptional_workers,
        # logging_file=args.logfile
    )

    scraping_manager.start_drivers()
    scraping_manager.start_exceptional_drivers()

    data = scraping_manager.scrape(
        URLs,
        is_scraping_general_info=args.is_scraping_general_info,
        is_scraping_about_tab=args.is_scraping_about_tab
    )

    save_data(data, args.savefile)