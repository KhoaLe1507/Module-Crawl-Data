URLS_FILEPATH = './input/urls.txt'
TOP100_URLS_FILEPATH = './input/top100_urls.txt'
SAVING_FILEPATH = './data/data.json'
TOP100_SAVING_FILEPATH = './data/data.json'
LOGGING_FILE = './logging/logging.log'

OPTIONS = ['start-maximized', "--disable-notifications"]
EXPERIMENT_OPTIONS = [
    ("prefs", {"profile.default_content_setting_values.notifications": 2})
]
NUM_WORKERS = 1
NUM_EXCEPTIONAL_WORKERS = 1

IS_SCRAPING_GENERAL_INFO = True
IS_SCRAPING_ABOUT_TAB = True