from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression


TRAIN_DIR = Path("/opt/ml/processing/train")
VALIDATION_DIR = Path("/opt/ml/processing/validation")
MODEL_DIR = Path("/opt/ml/processing/model")


def main() -> None:
    train_path = TRAIN_DIR / "train.csv"
    validation_path = VALIDATION_DIR / "validation.csv"

    print(f"Reading training data from {train_path}")
    if validation_path.exists():
        print(f"Validation data available at {validation_path}")

    df = pd.read_csv(train_path)

    X = df[["x1", "x2"]]
    y = df["target"]

    model = LinearRegression()
    model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "model.joblib"
    joblib.dump(model, model_path)

    print(f"Saved model to {model_path}")
    print("Training complete.")


if __name__ == "__main__":
    main()