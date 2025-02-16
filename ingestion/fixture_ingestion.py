import pandas as pd
import requests
from credentials import API_KEY, HEADERS
from config import all_leagues, seasons
import json
import os

def get_ids(df):
    id_types = ["fixture_id", "teams_home_id", "teams_away_id", "fixture_venue_id", "league_season", "league_id"]
    for id_type in id_types:
        unique_values = list(set(df[id_type])) 
        os.makedirs("data/ids/", exist_ok=True)
        pd.DataFrame({f"{id_type}s": unique_values}).to_csv(f"data/ids/{id_type}s.csv", index=False)



def get_league_fixtures(league, year):
    url = "https://v3.football.api-sports.io/fixtures"

    params = {
        "league": league, 
        "season": year  
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    fixtures = data.get("response", [])
    df = pd.json_normalize(fixtures)
    df.columns = [col.replace('.', '_') for col in df.columns]
    return df

def get_all_league_fixtures():
    all_fixtures_df = pd.DataFrame()
    for league_id in all_leagues:
        for season in seasons:
            df = get_league_fixtures(league_id, season)
            all_fixtures_df = pd.concat([all_fixtures_df, df], ignore_index=True)

    os.makedirs("data/", exist_ok=True)
    all_fixtures_df.to_csv("data/fixtures.csv", index=False)
    get_ids(all_fixtures_df)


if __name__=='__main__':
    get_all_league_fixtures()