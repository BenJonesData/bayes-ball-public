import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple
import tf_keras as tfk
import tqdm


class EpochProgressBar(tfk.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.epochs = self.params.get("epochs", 1)
        self.progress_bar = tqdm(
            total=self.epochs, desc="Training Progress", unit="epoch"
        )

    def on_epoch_end(self, epoch, logs=None):
        self.progress_bar.update(1)

    def on_train_end(self, logs=None):
        self.progress_bar.close()


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
