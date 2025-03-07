import calendar
import json
import os
import re
import time
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

from src.ingestion.sportmonks.config import BASE_URL, HEADERS, SAVE_LOCATION


def get_all_coaches_populate():
    all_coaches = []
    page = 1

    while True:
        endpoint_url = (
            f"{BASE_URL}/coaches?filters=populate&page={page}&per_page=1000"
        )
        response = requests.get(endpoint_url, headers=HEADERS)

        if response.status_code == 200:
            coaches = response.json()
            coaches = coaches.get("data", [])

            if not coaches:
                break

            all_coaches.extend(coaches)

            logger.info(f"Page {page} retrieved with {len(coaches)}.")
            page += 1

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}all_coaches.json", "w") as f:
        json.dump(all_coaches, f)


def get_all_coaches_with_statistics():
    include = "country;teams;statistics;nationality;trophies;player"

    all_coaches = []
    page = 1

    while True:
        endpoint_url = (
            f"{BASE_URL}/coaches?include={include}&page={page}&per_page=50"
        )
        response = requests.get(endpoint_url, headers=HEADERS)

        if response.status_code == 200:
            coaches = response.json()
            coaches = coaches.get("data", [])

            if not coaches:
                break

            all_coaches.extend(coaches)

            logger.info(f"Page {page} retrieved with {len(coaches)}.")
            page += 1

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}all_coaches_with_stats.json", "w") as f:
        json.dump(all_coaches, f)


if __name__ == "__main__":
    get_all_coaches_with_statistics()
