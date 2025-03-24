import logging
import os


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
        logging.info(args)

    @classmethod
    def error(cls, *args) -> None:
        logging.error(args)

    @classmethod
    def close(cls) -> None:
        logging.shutdown()
