class Config:
    input_folder: str
    output_folder: str
    secret_folder: str
    export_to_gcs: bool
    bucket_name: str

    @classmethod
    def set_configs(cls, configs):
        cls.input_folder = configs["input_folder"]
        cls.output_folder = configs["output_folder"]
        cls.secret_folder = configs["secret_folder"]
        cls.bucket_name = configs["bucket_name"]
        cls.export_to_gcs = configs["export_to_gcs"]
