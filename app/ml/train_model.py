"""
Standalone training script -- NOT imported by the API at runtime.

Run manually once you have a crop cycle or two of logged sensor + irrigation
data exported to CSV (see app/services/analytics_service.py for an export
helper), e.g.:

    python -m app.ml.train_model --csv data/tray_history.csv

Expected CSV columns match FEATURE_ORDER in irrigation_model.py plus a
target column `actual_moisture_after_pct`.
"""
import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

from app.ml.irrigation_model import FEATURE_ORDER


def train(csv_path: str, output_path: str) -> None:
    df = pd.read_csv(csv_path)
    X = df[FEATURE_ORDER]
    y = df["actual_moisture_after_pct"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    print(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} (on {len(y_test)} held-out rows)")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Saved model to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to exported tray history CSV")
    parser.add_argument("--out", default="app/ml/artifacts/irrigation_model.joblib")
    args = parser.parse_args()
    train(args.csv, args.out)
