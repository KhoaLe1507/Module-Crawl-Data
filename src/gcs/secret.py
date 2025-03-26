from google.cloud import secretmanager
from src.utils.log import Log
from src.utils.config import Config
from typing import List


class GcsSecret:
    def __init__(self) -> None:
        # Khởi tạo client Secret Manager
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_name) -> str:
        secret_path = (
            f"projects/{Config.project_id}/secrets/{secret_name}/versions/latest"
        )
        try:
            response = self.client.access_secret_version(name=secret_path)
            return response.payload.data.decode("UTF-8")
        except Exception:
            Log.error(f"Không thể truy xuất Secret: {secret_name}")
            return ""

    def get_secret_list(self, secret_name) -> List[str]:
        return self.get_secret(secret_name).splitlines()
