import logging
import os
from colorama import Fore, Style
import traceback


class Log:
    @classmethod
    def init(cls, logging_file: str | None) -> None:
        if logging_file is not None:
            dirpath = os.path.dirname(os.path.abspath(logging_file))
            os.makedirs(dirpath, exist_ok=True)
            with open(logging_file, "w", encoding="utf-8"):
                pass
            logging.basicConfig(
                filename=logging_file,
                level=logging.INFO,
            )
        else:
            logging.basicConfig(level=logging.INFO)

    @classmethod
    def info(cls, *args) -> None:
        print(Fore.CYAN)
        logging.info(args)
        print(Style.RESET_ALL)

    @classmethod
    def error(cls, *args) -> None:
        print(Fore.RED)
        logging.error(args)
        print(Style.RESET_ALL)

    @classmethod
    def warn(cls, *args) -> None:
        print(Fore.YELLOW)
        logging.warning(args)
        print(Style.RESET_ALL)

    @classmethod
    def traceback(cls, e: Exception) -> None:
        print(Fore.RED)
        print("Traceback:")
        print(traceback.format_tb(e.__traceback__))
        print(Style.RESET_ALL)

    @classmethod
    def close(cls) -> None:
        logging.shutdown()
