import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression


def main() -> None:
    train_dir = Path(os.environ["SM_CHANNEL_TRAIN"])
    model_dir = Path(os.environ["SM_MODEL_DIR"])

    train_path = train_dir / "train.csv"
    print(f"Reading training data from {train_path}")

    df = pd.read_csv(train_path)

    X = df[["x1", "x2"]]
    y = df["target"]

    model = LinearRegression()
    model.fit(X, y)

    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.joblib"
    joblib.dump(model, model_path)

    print(f"Saved model to {model_path}")
    print("Training complete.")


if __name__ == "__main__":
    main()
