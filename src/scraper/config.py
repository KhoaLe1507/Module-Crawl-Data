class ScrapeConfig:
    input_folder: str = "input"
    output_folder: str = "output"
    secret_folder: str = "secrets"
    export_to_gcs: bool = False

    def __init__(self) -> None:
        self.platform: str = ""
        self.data_type: str = ""

    def check(self) -> None:
        """
        Check if the configuration is valid
        """
        pass
