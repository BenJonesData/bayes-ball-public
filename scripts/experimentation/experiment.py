import pandas as pd
import argparse
from src.experimentation import run_experiment

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--experiment_name",
        type=str,
        default="general-experiment",
        help="The experiment to attribute the reun to",
    )

    parser.add_argument(
        "--run_id",
        type=str,
        default=None,
        help="A unique id for the run",
    )

    parser.add_argument(
        "--run_description",
        type=str,
        default=None,
        help="A description for the run",
    )

    parser.add_argument(
        "--training_data_path",
        type=str,
        default="data/train_data.csv",
        help="Path of training data csv",
    )

    parser.add_argument(
        "--validation_data_path",
        type=str,
        default="data/val_data.csv",
        help="Path of validation data csv",
    )
    parser.add_argument(
        "--hidden_units",
        nargs="+",
        type=int,
        default=None,
        help="Structure of hidden layer as a list, e.g., 8 or 8 16",
    )
    parser.add_argument(
        "--learning_rate", type=float, default=0.001, help="Learning rate"
    )
    parser.add_argument(
        "--num_epochs", type=int, default=100, help="Number of epochs"
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=100,
        help="Number of forward passes when generating output distributions",
    )
    parser.add_argument(
        "--num_batches",
        type=int,
        default=1,
        help="Number of batches for training",
    )
    parser.add_argument(
        "--league_tag",
        type=str,
        default=None,
        help="The league intended for the model",
    )

    args = parser.parse_args()

    training_data = pd.read_csv(args.training_data_path)
    validation_data = pd.read_csv(args.validation_data_path)

    run_experiment(
        args.experiment_name,
        training_data,
        validation_data,
        args.hidden_units,
        args.learning_rate,
        args.num_epochs,
        args.num_samples,
        args.num_batches,
        args.league_tag,
        args.run_id,
        args.run_description,
        return_model=False,
    )
