class Config:
    input_folder: str
    output_folder: str
    secret_folder: str
    product_mode: bool
    bucket_name: str
    project_id: str

    @classmethod
    def set_configs(cls, configs):
        cls.input_folder = configs["input_folder"]
        cls.output_folder = configs["output_folder"]
        cls.secret_folder = configs["secret_folder"]
        cls.bucket_name = configs["bucket_name"]
        cls.product_mode = configs["product_mode"]
        cls.project_id = configs["project_id"]
