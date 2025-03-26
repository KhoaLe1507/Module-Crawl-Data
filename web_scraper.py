import os
import json
from typing import List, Dict, Any
import datetime
import time


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


class Config:
    def __init__(self) -> None:
        pass

    def check(self) -> None:
        """
        Check if the configuration is valid
        """
        pass


class ScrapeResult(object):
    def __init__(self, export_other: bool = True) -> None:
        self.export_other = export_other
        self.rename_dict: Dict[str, str] = {}
        self.other = {}

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        elif key in self.other:
            return self.other[key]
        else:
            self.other[key] = None
            return self.other[key]

    def __setitem__(self, key: str, value) -> None:
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self.other[key] = value

    def assign_from_dict(self, d: Dict) -> None:
        for key, value in d.items():
            self[key] = value

    def to_dict(self) -> Dict:
        d = self.__dict__.copy()
        d.pop("export_other")
        d.pop("rename_dict")

        if not self.export_other:
            d.pop("other")

        result = {}
        for src_key, value in d.items():
            dest_key = src_key
            if src_key in self.rename_dict:
                dest_key = self.rename_dict[src_key]
            if isinstance(value, ScrapeResult):
                value = value.to_dict()
            result[dest_key] = value

        return result


class WebScraper(object):
    def __init__(self, config: Config) -> None:
        self.config = config
        self.result: List = []

    def run(self, urls: List[str]) -> None:
        _ = urls

    def close(self) -> None:
        pass

    def export(self, filepath: str) -> None:
        if len(self.result) == 0:
            return

        d = self.result
        if isinstance(self.result[0], ScrapeResult):
            d = [obj.to_dict() for obj in self.result]

        dirpath = os.path.dirname(os.path.abspath(filepath))
        os.makedirs(dirpath, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=4, ensure_ascii=False)


# EOF
