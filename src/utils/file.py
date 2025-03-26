import datetime
import time
from typing import List
from src.scraper.result import ScrapeResult
import os
import json


def get_lines(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    return urls


def get_output_filename(platform: str, data_type: str):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    timestamp = int(time.time())

    filename = f"{platform}/year={year}/month={month}/day={day}/{platform}_{data_type}_{timestamp}.json"
    return filename


def export_json(data: List, output_filename: str) -> None:
    if len(data) == 0:
        return

    d = data
    if isinstance(data[0], ScrapeResult):
        d = [obj.to_dict() for obj in data]

    dirpath = os.path.dirname(os.path.abspath(output_filename))
    os.makedirs(dirpath, exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)


# EOF
