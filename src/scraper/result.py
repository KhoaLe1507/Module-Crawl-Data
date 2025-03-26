from typing import Dict, Any


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
