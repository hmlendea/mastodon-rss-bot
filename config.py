import json
import os
import shutil

CONFIG_FILE = "config.json"
SAMPLE_FILE = "sample.config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(SAMPLE_FILE):
            shutil.copy(SAMPLE_FILE, CONFIG_FILE)
            print(f"[INFO] '{CONFIG_FILE}' was missing. Created from '{SAMPLE_FILE}'.")
        else:
            raise FileNotFoundError(f"Missing '{CONFIG_FILE}' and no '{SAMPLE_FILE}' to copy from.")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config()

INCLUDE_AUTHOR = cfg["include_author"]
INCLUDE_LINK = cfg["include_link"]
INCLUDE_LINK_THUMBNAIL = cfg["include_link_thumbnail"]
USE_PRIVACY_FRONTENDS = cfg["use_privacy_frontends"]
USE_SHORTLINK = cfg["use_shortlink"]
MAXIMUM_TOOTS_COUNT = cfg["maximum_toots_count"]