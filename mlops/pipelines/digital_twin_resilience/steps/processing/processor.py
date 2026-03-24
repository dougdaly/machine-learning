from pathlib import Path
import numpy as np
import pandas as pd

input_dir = Path("/opt/ml/processing/input")
output_train = Path("/opt/ml/processing/output/train")
output_val = Path("/opt/ml/processing/output/validation")
output_test = Path("/opt/ml/processing/output/test")

output_train.mkdir(parents=True, exist_ok=True)
output_val.mkdir(parents=True, exist_ok=True)
output_test.mkdir(parents=True, exist_ok=True)

# Minimal synthetic fallback if no input file is present
csv_files = list(input_dir.glob("*.csv"))

if csv_files:
    df = pd.read_csv(csv_files[0])
else:
    n = 500
    rng = np.random.default_rng(42)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    y = 2.0 * x1 - 0.5 * x2 + rng.normal(scale=0.1, size=n)
    df = pd.DataFrame({"x1": x1, "x2": x2, "target": y})

train_end = int(len(df) * 0.7)
val_end = int(len(df) * 0.85)

df.iloc[:train_end].to_csv(output_train / "train.csv", index=False)
df.iloc[train_end:val_end].to_csv(output_val / "validation.csv", index=False)
df.iloc[val_end:].to_csv(output_test / "test.csv", index=False)

print("Processing complete.")
