import pandas as pd
from typing import Iterable, List
from loguru import logger
from collections import Counter


def _enrich_data_fduk(data: pd.DataFrame) -> pd.DataFrame:
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


def get_data_fduk(
    seasons: Iterable[int],
    leagues: List[str],
    columns: List[str],
    enrich: bool,
) -> None:
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
                data = data[columns]
                data.columns = [col.lower() for col in data.columns]
                if enrich:
                    data = _enrich_data_fduk(data)
                data_list.append(data)
                logger.info(
                    f"Sucessfully loaded data for {league} in {season_tag}"
                )
            except Exception as e:
                logger.info(
                    f"Error loading data for {league} in {season_tag}: {e}"
                )
                continue

    data_full = pd.concat(data_list)

    return data_full
