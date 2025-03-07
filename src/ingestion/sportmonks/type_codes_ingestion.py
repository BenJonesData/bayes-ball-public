import calendar
import json
import re
import time
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

from src.ingestion.sportmonks.config import BASE_URL, HEADERS, SAVE_LOCATION


def get_types():
    logger.info("Getting type lookup codes")
    all_types = []

    page = 1
    while True:
        endpoint_url = f"https://api.sportmonks.com/v3/core/types?&page={page}&per_page=50"
        response = requests.get(endpoint_url, headers=HEADERS)
        types = response.json()
        types = types.get("data", [])
        all_types.extend(types)

        page += 1

        if not types:
            break

    all_types = pd.json_normalize(all_types)

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    all_types.to_csv(f"{SAVE_LOCATION}/types_lookup.csv", index=False)
    logger.info("Type lookup codes saved")


if __name__ == "__main__":
    get_types()
