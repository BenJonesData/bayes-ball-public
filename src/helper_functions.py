import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple

def get_train_test(
    data: pd.DataFrame, test_size: int = 2, random_state: int = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    unique_groups = data.loc[:, "season"].unique()

    train_groups, test_groups = train_test_split(
        unique_groups, test_size=test_size, random_state=random_state
    )

    train_data = data.loc[data["season"].isin(train_groups)]
    test_data = data.loc[data["season"].isin(test_groups)]

    return train_data, test_data
