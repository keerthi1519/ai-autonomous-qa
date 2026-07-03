import json
from pathlib import Path

CONFIG_FILE = Path("config.json")


def load_config():
    if not CONFIG_FILE.exists():
        return {
            "base_url": "https://example.com",
            "browser": "chrome",
            "headless": False,
            "timeout": 10,
        }

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)