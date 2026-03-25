import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


MODEL_DIR = Path("/opt/ml/processing/model")
TEST_DIR = Path("/opt/ml/processing/test")
EVAL_DIR = Path("/opt/ml/processing/evaluation")


def main() -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / "model.joblib"
    test_path = TEST_DIR / "test.csv"
    metrics_path = EVAL_DIR / "metrics.json"

    print(f"Loading model from {model_path}")
    print(f"Loading test data from {test_path}")

    model = joblib.load(model_path)
    df = pd.read_csv(test_path)

    X = df[["x1", "x2"]]
    y = df["target"]

    predictions = model.predict(X)

    metrics = {
        "mse": float(mean_squared_error(y, predictions)),
        "mae": float(mean_absolute_error(y, predictions)),
        "n_test_rows": int(len(df)),
    }

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print("Evaluation complete.")
    print(json.dumps(metrics, indent=2))
    print(f"Wrote metrics to {metrics_path}")


if __name__ == "__main__":
    main()
