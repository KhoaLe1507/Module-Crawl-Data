class ScrapeConfig:
    def __init__(self) -> None:
        self.platform: str = ""
        self.data_type: str = ""

    def check(self) -> None:
        """
        Check if the configuration is valid
        """
        pass
