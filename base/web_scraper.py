import os
import json
from typing import List, Dict, Any
from log import Log


def get_lines(filepath: str) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    return urls


class Config:
    def __init__(self) -> None:
        self.logging_file: str | None = None

    def check(self) -> None:
        """
        Check if the configuration is valid
        """
        pass


class ScrapeResult(object):
    def __init__(self) -> None:
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
        result = self.__dict__.copy()
        for key, value in self.__dict__.items():
            if isinstance(value, ScrapeResult):
                result[key] = value.to_dict()

        return result


class WebScraper(object):
    def __init__(self, config: Config) -> None:
        Log.init(config.logging_file)
        self.config = config
        self.result: List = []

    def run(self, urls: List[str]) -> None:
        _ = urls

    def close(self) -> None:
        Log.close()

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
