import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

model_dir = Path("/opt/ml/processing/model")
test_dir = Path("/opt/ml/processing/test")
eval_dir = Path("/opt/ml/processing/evaluation")

eval_dir.mkdir(parents=True, exist_ok=True)

model = joblib.load(model_dir / "model.joblib")
df = pd.read_csv(test_dir / "test.csv")

X = df[["x1", "x2"]]
y = df["target"]
pred = model.predict(X)

metrics = {
    "mse": float(mean_squared_error(y, pred)),
    "mae": float(mean_absolute_error(y, pred)),
    "n_test_rows": int(len(df)),
}

with open(eval_dir / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(json.dumps(metrics, indent=2))
