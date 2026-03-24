import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

train_dir = Path(os.environ["SM_CHANNEL_TRAIN"])
model_dir = Path(os.environ["SM_MODEL_DIR"])

df = pd.read_csv(train_dir / "train.csv")
X = df[["x1", "x2"]]
y = df["target"]

model = LinearRegression()
model.fit(X, y)

model_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_dir / "model.joblib")

print("Training complete.")
