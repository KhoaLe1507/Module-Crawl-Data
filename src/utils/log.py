# import logging
# import os
from colorama import Fore, Style
import traceback


class Log:
    @classmethod
    def print(cls, color, tag: str, *args) -> None:
        print(color, f"[{tag}]", *args, Style.RESET_ALL)

    @classmethod
    def info(cls, *args) -> None:
        cls.print(Fore.BLUE, "INFO", *args)

    @classmethod
    def error(cls, *args) -> None:
        cls.print(Fore.RED, "ERROR", *args)

    @classmethod
    def warn(cls, *args) -> None:
        cls.print(Fore.YELLOW, "WARN", *args)

    @classmethod
    def start(cls, *args) -> None:
        cls.print(Fore.CYAN, "START", *args)

    @classmethod
    def finish(cls, *args) -> None:
        cls.print(Fore.GREEN, "FINISH", *args)

    @classmethod
    def exception(cls, e: Exception) -> None:
        print(Fore.RED, end=None)
        print("[TRACEBACK]")
        print("\n".join(traceback.format_tb(e.__traceback__)))
        print(e.__str__(), end=None)
        print(Style.RESET_ALL)
