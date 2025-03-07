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
from src.ingestion.sportmonks.league_codes_ingestion import get_leagues


def get_fixtures_from_period(league_id, start_date, end_date):
    fixtures = []
    current_year = datetime.now().year

    filters = f"fixtureLeagues:{league_id}"
    include = "  participants;round;stage;group;league;season;venue;state;weatherReport;lineups;coaches;periods;participants;statistics;metadata;formations;sidelined;scores"
    endpoint = f"/fixtures/between/{start_date}/{end_date}"

    page = 1
    while True:
        endpoint_url = f"{BASE_URL}{endpoint}?filters={filters}&include={include}&page={page}&per_page=50"
        response = requests.get(endpoint_url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            fixtures_by_page = data.get("data", [])

            if not fixtures_by_page:
                break

            fixtures.extend(fixtures_by_page)
            page += 1
        else:
            logger.error(
                f"Failed to retrieve data. Status code:", response.status_code
            )
            break

    return fixtures


def get_all_fixtures_by_league(league_id):
    fixtures = []
    current_year = datetime.now().year

    for year in range(2000, current_year + 1):
        for month in range(1, 13):
            start_date = f"{year}-{str(month).zfill(2)}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{str(month).zfill(2)}-{last_day}"

            fixtures_by_period = get_fixtures_from_period(
                league_id, start_date, end_date
            )
            logger.info(
                f"Ingested for league: {league_id} between {start_date} and {end_date} with {len(fixtures_by_period)} games"
            )

            fixtures.extend(fixtures_by_period)

    os.makedirs(f"{SAVE_LOCATION}fixtures", exist_ok=True)
    with open(f"data/fixtures/{league_id}_fixtures.json", "w") as f:
        json.dump(fixtures, f)

    return fixtures


def merge_fixtures_by_league(
    split_fixture_location=f"{SAVE_LOCATION}fixtures",
):
    all_fixtures = []
    for fixtures_file in os.listdir(f"{SAVE_LOCATION}fixtures"):
        with open(f"{SAVE_LOCATION}fixtures/{fixtures_file}", "r") as file:
            fixtures = json.load(file)
            all_fixtures.extend(fixtures)

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}all_fixtures.json", "w") as f:
        json.dump(all_fixtures, f)


def get_league_ids():
    if not os.path.exists(f"{SAVE_LOCATION}leagues_lookup.csv"):
        get_leagues()

    leagues = pd.read_csv(f"{SAVE_LOCATION}leagues_lookup.csv")
    league_ids = list(set(leagues["id"]))
    return league_ids


def get_all_fixtures():
    # This function breaks because of limits in the API requests
    fixtures = []

    league_ids = get_league_ids()
    logger.info(f"League ids: {league_ids}")
    for league_id in league_ids:
        fixtures_by_league = get_all_fixtures_by_league(league_id)
        fixtures.extend(fixtures_by_league)

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}all_fixtures.json", "w") as f:
        json.dump(fixtures, f)


if __name__ == "__main__":
    # Ideally use get_all_fixtures() but limited by API requests

    league_ids = get_league_ids()

    # Manually feed in random IDs
    league_id = league_ids[0]
    fixtures_by_league = get_all_fixtures_by_league(league_id)
