import os
import json

API_KEYS = json.loads(os.environ.get("APIFY_KEYS", "[]"))