import numpy as np
import tf_keras as tfk
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss
import mlflow
from scipy.stats import ttest_1samp
from typing import List

from src.bayesian_nn import (
    extract_features_and_target,
    make_dataset,
    create_bnn_model,
    model_inference,
)
from src.priors_posteriors import std_normal_prior, std_normal_posterior
from src.helper_functions import EpochProgressBar  # , bootstrap_mse


def run_experiment(
    experiment_name: str,
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    hidden_units: List[int] = None,
    learning_rate: float = 0.001,
    num_epochs: int = 100,
    num_samples: int = 100,
    num_batches: int = 1,
    league_tag: str = None,
    run_id: str = None,
    run_description: str = None,
    return_model: bool = False,
) -> None | tfk.Model:

    mlflow.set_tracking_uri("http://localhost:5001")
    mlflow.set_experiment(experiment_name)
    mlflow.start_run()

    train_seasons = list(train_data["season"].drop_duplicates())
    val_seasons = list(val_data["season"].drop_duplicates())

    train_data = train_data.drop(columns=["season"])
    val_data = val_data.drop(columns=["season"])

    feature_names = [col for col in train_data.columns if col != "h_win"]
    n_train = len(train_data)
    batch_size = int(len(train_data) / num_batches)

    X_train, y_train = extract_features_and_target(
        train_data, feature_names, "h_win"
    )
    X_val, y_val = extract_features_and_target(
        val_data.drop(columns="bookies_prob"), feature_names, "h_win"
    )

    train_dataset = make_dataset(X_train, y_train, n_train, batch_size)

    model = create_bnn_model(
        feature_names=feature_names,
        hidden_units=hidden_units,
        prior=std_normal_prior,
        posterior=std_normal_posterior,
        n_train=n_train,
    )

    model.compile(
        optimizer=tfk.optimizers.legacy.RMSprop(learning_rate=learning_rate),
        loss=tfk.losses.MeanSquaredError(),
        metrics=[tfk.metrics.MeanSquaredError()],
    )

    model.fit(
        train_dataset,
        epochs=num_epochs,
        callbacks=[EpochProgressBar()],
        verbose=0,
    )

    sampled_train_probs = model_inference(
        model, X_train, num_samples, tag="training"
    )
    mean_train_probs = np.mean(sampled_train_probs, axis=0)
    train_mse = brier_score_loss(y_train, mean_train_probs)
    train_auc = roc_auc_score(y_train, mean_train_probs)

    sampled_val_probs = model_inference(
        model, X_val, num_samples, tag="validation"
    )
    mean_val_probs = np.mean(sampled_val_probs, axis=0)
    val_mse = brier_score_loss(val_data["h_win"], mean_val_probs)
    # val_mse_ci = bootstrap_mse(val_data["h_win"], mean_val_probs)
    val_auc = roc_auc_score(val_data["h_win"], mean_val_probs)

    bookies_val_mse = brier_score_loss(
        val_data["h_win"], val_data["bookies_prob"]
    )
    bookies_val_auc = roc_auc_score(
        val_data["h_win"], val_data["bookies_prob"]
    )
    val_mse_diff = val_mse - bookies_val_mse
    val_auc_diff = val_auc - bookies_val_auc

    val_squared_errors = (mean_val_probs - val_data["h_win"]) ** 2
    bookies_squared_errors = (
        val_data["bookies_prob"] - val_data["h_win"]
    ) ** 2
    pairwise_differences = bookies_squared_errors - val_squared_errors

    _, p_val_two_tailed = ttest_1samp(
        pairwise_differences, 0, alternative="greater"
    )

    mlflow.set_tags(
        {
            "run_id": run_id,
            "run_description": run_description,
            "league": league_tag,
        }
    )

    mlflow.log_params(
        {
            "model_type": "bayesian_nn",
            "prior": std_normal_prior.__name__,
            "posterior": std_normal_posterior.__name__,
            "feature_names": feature_names,
            "num_features": len(feature_names),
            "train_seasons": train_seasons,
            "num_train_seasons": len(train_seasons),
            "val_seasons": val_seasons,
            "num_val_seasons": len(val_seasons),
            "n_train": n_train,
            "num_batches": num_batches,
            "hidden_units": hidden_units,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
            "num_samples": num_samples,
        }
    )

    mlflow.log_metrics(
        {
            "train_mse": train_mse,
            "train_auc": train_auc,
            "val_mse": val_mse,
            # "val_mse_5_percentile": val_mse_ci[0],
            # "val_mse_95_percentile": val_mse_ci[1],
            "val_auc": val_auc,
            "bookies_val_mse": bookies_val_mse,
            "bookies_val_auc": bookies_val_auc,
            "val_mse_diff": val_mse_diff,
            "val_auc_diff": val_auc_diff,
            "beat_bookies_pvalue": p_val_two_tailed,
        }
    )

    mlflow.end_run()

    if return_model:
        return model
