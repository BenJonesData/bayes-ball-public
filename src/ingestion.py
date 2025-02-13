import pandas as pd
from typing import Iterable, List
from loguru import logger
from collections import Counter

DESIRED_COLS = [
    "season",
    "Div",
    "Date",
    "HomeTeam",
    "AwayTeam",
    "B365H",
    "B365D",
    "B365A",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
    "HS",
    "AS",
    "HST",
    "AST",
    "HC",
    "AC",
    "HF",
    "AF",
    "HY",
    "AY",
    "HR",
    "AR",
]
LEAGUES = [
    "E0",
    "E1",
    "E2",
    "E3",
    "EC",
    "SC0",
    "SC1",
    "SC2",
    "SC3",
    "D1",
    "D2",
    "I1",
    "I2",
    "SP1",
    "SP2",
    "F1",
    "F2",
]


def enrich_data(data: pd.DataFrame) -> pd.DataFrame:
    output_data = data.copy()

    teams = list(output_data["hometeam"].drop_duplicates())
    half_way_point = len(teams) - 1

    team_counter = Counter()
    game_num_h = []
    game_num_a = []
    for _, row in output_data.iterrows():
        team_counter[row["hometeam"]] += 1
        game_num_h.append(team_counter[row["hometeam"]])
        team_counter[row["awayteam"]] += 1
        game_num_a.append(team_counter[row["awayteam"]])
    output_data["game_num_h"] = game_num_h
    output_data["game_num_a"] = game_num_a

    output_data["season_half_h"] = 1
    output_data["season_half_a"] = 1
    output_data.loc[
        output_data["game_num_h"] > half_way_point, "season_half_h"
    ] = 2
    output_data.loc[
        output_data["game_num_a"] > half_way_point, "season_half_a"
    ] = 2

    return output_data


def get_data(seasons: Iterable[int], leagues: List[str] | str = "all") -> None:
    if leagues == "all":
        leagues = LEAGUES
    elif not set(leagues).issubset(set(LEAGUES)):
        raise ValueError(
            f"""
            Invalid league provided. Please chose one or more from {LEAGUES}
        """
        )

    data_list = []
    for start_y in seasons:
        season = str(start_y) + str(start_y + 1)
        season_tag = str(start_y) + "_" + str(start_y + 1)
        for league in leagues:
            url = (
                "https://www.football-data.co.uk/mmz4281/"
                + f"{season}/{league}.csv"
            )
            try:
                data = pd.read_csv(url)
                data["season"] = season_tag
                data = data[DESIRED_COLS]
                data.columns = [col.lower() for col in data.columns]
                processed_data = enrich_data(data)
                data_list.append(processed_data)
                logger.info(
                    f"Sucessfully loaded data for {league} in {season_tag}"
                )
            except Exception as e:
                logger.info(
                    f"Error loading data for {league} in {season_tag}: {e}"
                )
                continue

    data_full = pd.concat(data_list)
    data_full.to_csv("data/raw_games.csv", index=False)
    logger.info("All available data loaded and saved to data/raw_games.csv")


if __name__ == "__main__":
    get_data(range(10, 25))
