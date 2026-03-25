import json
from pathlib import Path

import numpy as np
import pandas as pd


INPUT_DIR = Path("/opt/ml/processing/input")
CONFIG_DIR = Path("/opt/ml/processing/config")

OUTPUT_TRAIN_DIR = Path("/opt/ml/processing/output/train")
OUTPUT_VALIDATION_DIR = Path("/opt/ml/processing/output/validation")
OUTPUT_TEST_DIR = Path("/opt/ml/processing/output/test")


def load_request_config() -> dict:
    request_path = CONFIG_DIR / "request.json"

    if not request_path.exists():
        print(f"No request config found at {request_path}. Using defaults.")
        return {}

    with open(request_path, "r") as f:
        config = json.load(f)

    print(f"Loaded request config from {request_path}:")
    print(json.dumps(config, indent=2))
    return config


def make_synthetic_data(
    start_date: str = None,
    end_date: str = None,
    n_rows: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    x1 = rng.normal(loc=0.0, scale=1.0, size=n_rows)
    x2 = rng.normal(loc=0.0, scale=1.0, size=n_rows)
    noise = rng.normal(loc=0.0, scale=0.2, size=n_rows)
    target = 2.0 * x1 - 0.5 * x2 + noise

    df = pd.DataFrame(
        {
            "x1": x1,
            "x2": x2,
            "target": target,
        }
    )

    if start_date and end_date:
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)

        if start_ts > end_ts:
            raise ValueError(f"start_date {start_date} is after end_date {end_date}")

        df["timestamp"] = pd.date_range(start=start_ts, end=end_ts, periods=n_rows)

    return df


def load_input_data(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if not csv_files:
        print("No input CSV found. Generating synthetic data.")
        return make_synthetic_data(start_date=start_date, end_date=end_date)

    if start_date and end_date:
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)

        for csv_file in csv_files:
            df = pd.read_csv(csv_file)

            if "timestamp" not in df.columns:
                continue

            df["timestamp"] = pd.to_datetime(df["timestamp"])
            mask = (df["timestamp"] >= start_ts) & (df["timestamp"] <= end_ts)
            filtered_df = df.loc[mask].copy()

            if not filtered_df.empty:
                filtered_df = filtered_df.sort_values("timestamp").reset_index(drop=True)
                print(f"Found input file: {csv_file} with data in date range")
                return filtered_df

        print("No input CSV found with data in the specified date range. Generating synthetic data.")
        return make_synthetic_data(start_date=start_date, end_date=end_date)

    print(f"Found input file: {csv_files[0]}")
    return pd.read_csv(csv_files[0])


def main() -> None:
    OUTPUT_TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TEST_DIR.mkdir(parents=True, exist_ok=True)

    request_config = load_request_config()
    start_date = request_config.get("start_date")
    end_date = request_config.get("end_date")

    df = load_input_data(start_date=start_date, end_date=end_date)

    train_end = int(len(df) * 0.70)
    validation_end = int(len(df) * 0.85)

    train_df = df.iloc[:train_end].copy()
    validation_df = df.iloc[train_end:validation_end].copy()
    test_df = df.iloc[validation_end:].copy()

    train_path = OUTPUT_TRAIN_DIR / "train.csv"
    validation_path = OUTPUT_VALIDATION_DIR / "validation.csv"
    test_path = OUTPUT_TEST_DIR / "test.csv"

    train_df.to_csv(train_path, index=False)
    validation_df.to_csv(validation_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"Wrote train data to {train_path}")
    print(f"Wrote validation data to {validation_path}")
    print(f"Wrote test data to {test_path}")
    print("Processing complete.")


if __name__ == "__main__":
    main()