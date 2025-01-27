"""
Script containing functions to take in game data downloaded in ingestion.py
and transform into a dataset containing games from the second half of seasons
with features derived from the first half of seasons. Running this script will
create such a dataset with the two covid seasons removed.
"""

import pandas as pd
from typing import List
from loguru import logger


def create_dataset(data: pd.DataFrame, exclude_seasons: List[str] = None) -> None:
    """
    Creates and saves a dataset of games from the second half of seasons with
    aggregated stats from the first half of the season.

    Args:
        data (pd.DataFrame): The game data with a season half column.
        exclude_seasons (List[str]): a list of seasons to remove.
    """
    data = data.copy()
    logger.info("Starting dataset creation")

    if exclude_seasons is not None:
        data = data[~data["season"].isin(exclude_seasons)]
        logger.info(f"Sucessfully removed seasons: {exclude_seasons}")

    home_h1_data = data.loc[
        data["season_half_h"] == 1,
        [
            "season",
            "div",
            "hometeam",
            "fthg",
            "hthg",
            "hs",
            "hst",
            "hc",
            "hf",
            "hy",
            "hr",
            "ftag",
            "htag",
            "as",
            "ast",
            "ac",
            "af",
            "ay",
            "ar",
        ],
    ]
    away_h1_data = data.loc[
        data["season_half_a"] == 1,
        [
            "season",
            "div",
            "awayteam",
            "ftag",
            "htag",
            "as",
            "ast",
            "ac",
            "af",
            "ay",
            "ar",
            "fthg",
            "hthg",
            "hs",
            "hst",
            "hc",
            "hf",
            "hy",
            "hr",
        ],
    ]

    # for home teams, home stats are for and away stats are against
    home_h1_data.rename(
        columns={
            "hometeam": "team",
            "fthg": "avg_goals_scored",
            "hthg": "avg_ht_goals_scored",
            "hs": "avg_shots",
            "hst": "avg_sot",
            "hc": "avg_corners",
            "hf": "avg_fouls",
            "hy": "avg_yellows",
            "hr": "avg_reds",
            "ftag": "avg_goals_conceded",
            "htag": "avg_ht_goals_conceded",
            "as": "avg_shots_faced",
            "ast": "avg_sot_faced",
            "ac": "avg_corners_faced",
            "af": "avg_fouls_against",
            "ay": "avg_yellows_against",
            "ar": "avg_reds_against",
        },
        inplace=True,
    )

    # for away teams, home stats are against and away stats are for
    away_h1_data.rename(
        columns={
            "awayteam": "team",
            "ftag": "avg_goals_scored",
            "htag": "avg_ht_goals_scored",
            "as": "avg_shots",
            "ast": "avg_sot",
            "ac": "avg_corners",
            "af": "avg_fouls",
            "ay": "avg_yellows",
            "ar": "avg_reds",
            "fthg": "avg_goals_conceded",
            "hthg": "avg_ht_goals_conceded",
            "hs": "avg_shots_faced",
            "hst": "avg_sot_faced",
            "hc": "avg_corners_faced",
            "hf": "avg_fouls_against",
            "hy": "avg_yellows_against",
            "hr": "avg_reds_against",
        },
        inplace=True,
    )
    logger.info("Home and away dataframes created succesfully")

    # create a column for proportion of matches played at home
    home_h1_data["prop_h"] = 1
    away_h1_data["prop_h"] = 0

    all_h1_data = pd.concat([home_h1_data, away_h1_data])
    stats_h1 = (
        all_h1_data.groupby(["season", "div", "team"]).mean().reset_index()
    )
    logger.info("Home and away dataframes succesfully combined and grouped")

    results_h2 = data.loc[
        (data["season_half_h"] == 2) & (data["season_half_a"] == 2),
        ["season", "div", "date", "hometeam", "awayteam", "ftr"],
    ]
    results_h2.rename(
        columns={"hometeam": "h_team", "awayteam": "a_team"}, inplace=True
    )

    results_h2 = results_h2.merge(
        stats_h1.add_prefix("h_"),
        left_on=["season", "div", "h_team"],
        right_on=["h_season", "h_div", "h_team"],
        how="inner",
    )
    results_h2 = results_h2.merge(
        stats_h1.add_prefix("a_"),
        left_on=["season", "div", "a_team"],
        right_on=["a_season", "a_div", "a_team"],
        how="inner",
    )
    logger.info("Team stats succesfully merged onto game data")

    # clean up duplicate columns
    results_h2.drop(
        columns=["h_season", "h_div", "a_season", "a_div"], inplace=True
    )
    logger.info("Duplicate columns successfully dropped")

    results_h2.to_csv("data/processed_data.csv", index=False)
    logger.info("Dataset created and saved to data/processed_data.csv")
  

if __name__ == "__main__":
    data = pd.read_csv("data/raw_games.csv")
    # remove covid seasons
    create_dataset(data, exclude_seasons=["19_20", "20_21"])
