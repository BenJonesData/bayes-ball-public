import numpy as np
import tensorflow as tf
import tf_keras as tfk
import tensorflow_probability as tfp
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Tuple


tfd = tfp.distributions
tfpl = tfp.layers


def extract_features_and_target(
    data: pd.DataFrame, feature_names: List[str], target: str
) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    X = {
        feature: data[feature].values.astype(np.float32)
        for feature in feature_names
    }
    y = data[target].values.astype(np.float32)

    return X, y


def make_dataset(
    X: Dict[str, np.ndarray], y: np.ndarray, buffer_size: int, batch_size: int
) -> tf.data.Dataset:
    dataset = (
        tf.data.Dataset.from_tensor_slices((X, y))
        .shuffle(buffer_size=buffer_size)
        .batch(batch_size)
        .cache()
    )

    return dataset


def create_bnn_model(
    feature_names: List[str],
    hidden_units: List[int],
    prior: callable,
    posterior: callable,
    n_train: int,
) -> tfk.Model:

    inputs = {}
    for feature_name in feature_names:
        inputs[feature_name] = tfk.layers.Input(
            name=feature_name, shape=(1,), dtype=tf.float32
        )

    features = tfk.layers.concatenate(list(inputs.values()))
    features = tfk.layers.BatchNormalization()(features)

    if hidden_units is not None:
        for units in hidden_units:
            features = tfp.layers.DenseVariational(
                units=units,
                make_prior_fn=prior,
                make_posterior_fn=posterior,
                kl_weight=1 / n_train,
                activation="sigmoid",
            )(features)

    outputs = tfp.layers.DenseVariational(
        units=1,
        make_prior_fn=prior,
        make_posterior_fn=posterior,
        kl_weight=1 / n_train,
        activation="sigmoid",
    )(features)

    return tfk.Model(inputs=inputs, outputs=outputs)


def model_inference(
    model: tfk.Model, X: Dict[str, np.ndarray], num_samples: str, tag: str = None
) -> np.array:
    if tag is not None:
        tag = tag.title()
        tag += " "

    sampled_probs = np.stack(
        [
            model(X, training=True).numpy().flatten()
            for _ in tqdm(range(num_samples), desc=f"{tag}Output Sampling Progress")
        ]
    )

    return sampled_probs


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
