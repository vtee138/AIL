"""Dự đoán PM2.5 ở Hà Nội bằng Ridge với bộ đặc trưng F4.

Chạy: python run.py
"""

from pathlib import Path

import holidays
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
HORIZONS = [1, 6, 12, 24, 48]  # dự đoán sau từng này giờ
WEATHER = ["temp", "rh", "wind", "pressure", "precip", "clouds", "uv"]
ALPHA = 1554.6366680730962  # giá trị Ridge F4 đã chọn trong DAP


def make_features(data):
    """Mỗi hàng là thông tin có sẵn tại thời điểm t hoặc trước t."""
    pm = data["pm25"]
    features = {}

    # Nồng độ PM2.5 hiện tại và các giờ trước đó.
    for lag in [0, *range(1, 25), 48, 72, 168]:
        features[f"pm25_lag{lag}"] = pm.shift(lag)
    for window in [3, 6, 12, 24]:
        recent = pm.rolling(window)
        features[f"pm25_mean{window}"] = recent.mean()
        features[f"pm25_std{window}"] = recent.std()
        features[f"pm25_min{window}"] = recent.min()
        features[f"pm25_max{window}"] = recent.max()

    # Giờ, thứ, mùa trong năm, cuối tuần và ngày lễ Việt Nam.
    t = data.index
    for name, value, period in [
        ("hour", t.hour, 24),
        ("dow", t.dayofweek, 7),
        ("doy", t.dayofyear, 365.25),
    ]:
        features[f"{name}_sin"] = np.sin(2 * np.pi * value / period)
        features[f"{name}_cos"] = np.cos(2 * np.pi * value / period)
    features["is_weekend"] = (t.dayofweek >= 5).astype(int)
    vn_holidays = holidays.country_holidays("VN", years=range(t.year.min(), t.year.max() + 1))
    features["is_holiday"] = [int(day in vn_holidays) for day in t.date]

    # Thời tiết đo tại t và trước t; không dùng thời tiết tương lai.
    for name in WEATHER:
        series = data[name]
        for lag in [0, 1, 3, 6, 12, 24]:
            features[f"{name}_lag{lag}"] = series.shift(lag)
        for window in [6, 24]:
            recent = series.rolling(window)
            features[f"{name}_mean{window}"] = recent.mean()
            features[f"{name}_std{window}"] = recent.std()
            features[f"{name}_min{window}"] = recent.min()
            features[f"{name}_max{window}"] = recent.max()
    return pd.DataFrame(features, index=data.index)


def main():
    data = pd.read_csv(HERE / "data" / "hanoi_pm25_weather.csv", parse_dates=["time"])
    data = data.set_index("time").sort_index()
    x = make_features(data)
    y = pd.DataFrame({f"h{h}": data["pm25"].shift(-h) for h in HORIZONS})

    # Chỉ giữ các hàng có đầy đủ đặc trưng và cả 5 giá trị cần dự đoán.
    valid = x.notna().all(axis=1) & y.notna().all(axis=1)
    x, y = x.loc[valid], y.loc[valid]

    # Chia theo thời gian. 48 giờ đệm bảo đảm nhãn huấn luyện không nằm trong 2025.
    test_start = pd.Timestamp("2025-01-01")
    train = x.index < test_start - pd.Timedelta(hours=max(HORIZONS))
    test = x.index >= test_start
    results = []
    predictions = pd.DataFrame(index=x.index[test])

    for h in HORIZONS:
        column = f"h{h}"
        model = make_pipeline(StandardScaler(), Ridge(alpha=ALPHA))
        model.fit(x.loc[train], y.loc[train, column])
        predicted = model.predict(x.loc[test])
        actual = y.loc[test, column]

        results.append({
            "horizon_hours": h,
            "n_test": len(actual),
            "rmse": mean_squared_error(actual, predicted) ** 0.5,
            "mae": mean_absolute_error(actual, predicted),
            "r2": r2_score(actual, predicted),
        })
        predictions[f"actual_h{h}"] = actual
        predictions[f"predicted_h{h}"] = predicted

    output = HERE / "output"
    output.mkdir(exist_ok=True)
    summary = pd.DataFrame(results).round(3)
    summary.to_csv(output / "metrics.csv", index=False)
    predictions.rename_axis("time").round(3).to_csv(output / "predictions.csv")
    print(summary.to_string(index=False))
    print(f"\nSaved results to: {output}")


if __name__ == "__main__":
    main()
