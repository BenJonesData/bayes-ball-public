import argparse

from src.ingestion import get_data_fduk


DEFAULT_COLS = [
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
LEAGUES = ["E0"]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start_year",
        type=int,
        default=10,
        help="The start of the first season to be included e.g. 10 for the 2010/11 season",
    )

    parser.add_argument(
        "--end_year",
        type=int,
        default=25,
        help="The end of the last season to be included e.g. 25 for the 2024/25 season",
    )

    parser.add_argument(
        "--leagues",
        nargs="+",
        type=str,
        default=["E0"],
        help="List of leagues to include",
    )

    parser.add_argument(
        "--columns",
        nargs="+",
        type=str,
        default=DEFAULT_COLS,
        help="List of columns to include",
    )

    parser.add_argument(
        "--save_filename",
        type=str,
        default="ingested_fduk_data",
        help="The name to call the saved file (omit .csv)",
    )

    parser.add_argument(
        "--enrich",
        type=bool,
        default=False,
        help="Whether or not to add game numbers and season halves as columns for home and away team",
    )

    args = parser.parse_args()

    data = get_data_fduk(
        range(args.start_year, args.end_year),
        args.leagues,
        args.columns,
        args.enrich,
    )

    data.to_csv(f"data/{args.save_filename}.csv")
