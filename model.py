"""Bước 4: tạo đặc trưng F4, huấn luyện và đánh giá Ridge.

Chạy: python model.py

Đầu vào: data/hanoi_pm25_weather.csv do preprocess.py tạo.
Đầu ra: output/metrics.csv và output/predictions.csv.
Mỗi mốc 1, 6, 12, 24, 48 giờ có một mô hình Ridge riêng.
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
# Horizon h nghĩa là dự đoán PM2.5 tại thời điểm t+h từ thông tin ở t.
HORIZONS = [1, 6, 12, 24, 48]
WEATHER = ["temp", "rh", "wind", "pressure", "precip", "clouds", "uv"]
# Alpha càng lớn thì Ridge càng ép hệ số nhỏ. Bài này dùng một giá trị cố định,
# không tìm alpha bằng dữ liệu kiểm tra năm 2025.
ALPHA = 1554.6366680730962  # hệ số điều chuẩn cố định cho bài thực hành


def make_features(data):
    """Tạo 150 đặc trưng F4 cho từng giờ t, không đọc dữ liệu sau t.

    Bao gồm 44 đặc trưng PM2.5, 8 đặc trưng lịch và 98 đặc trưng thời tiết.
    Các hàng đầu thiếu lag dài sẽ được loại sau trong main().
    """
    pm = data["pm25"]
    # Gom Series vào dict rồi tạo DataFrame một lần để mã gọn và tránh thêm
    # hàng trăm cột vào DataFrame từng bước.
    features = {}

    # shift(0) là PM2.5 tại t; shift(24) là PM2.5 cách 24 giờ.
    # Các lag 48, 72, 168 bổ sung trí nhớ 2-3 ngày và 1 tuần.
    for lag in [0, *range(1, 25), 48, 72, 168]:
        features[f"pm25_lag{lag}"] = pm.shift(lag)
    # rolling(window) tính trên cửa sổ kết thúc ở t, nên chỉ dùng hiện tại
    # và quá khứ. Mean/std/min/max tóm tắt mức độ và độ dao động gần đây.
    for window in [3, 6, 12, 24]:
        recent = pm.rolling(window)
        features[f"pm25_mean{window}"] = recent.mean()
        features[f"pm25_std{window}"] = recent.std()
        features[f"pm25_min{window}"] = recent.min()
        features[f"pm25_max{window}"] = recent.max()

    # Mã hóa chu kỳ bằng sin/cos: 23:00 gần 00:00 và Chủ nhật gần thứ Hai
    # trên vòng thời gian. Biến cuối tuần/ngày lễ là 0 hoặc 1.
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

    # Với mỗi biến thời tiết, dùng số đo tại t và các mốc quá khứ.
    # Không dùng thời tiết tại t+h, vì ở thời điểm dự đoán chưa biết giá trị đó.
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
    """Nạp dữ liệu, chia theo thời gian, fit Ridge và xuất kết quả kiểm tra."""
    # Đọc CSV cục bộ của AIL. Dùng time làm chỉ số để shift và chia tập theo giờ.
    data = pd.read_csv(HERE / "data" / "hanoi_pm25_weather.csv", parse_dates=["time"])
    data = data.set_index("time").sort_index()
    x = make_features(data)
    # shift(-h) đưa PM2.5 ở tương lai t+h về cùng hàng với đặc trưng tại t.
    # Đây là nhãn cần dự đoán, không phải một cột đầu vào của mô hình.
    y = pd.DataFrame({f"h{h}": data["pm25"].shift(-h) for h in HORIZONS})

    # Giữ cùng một tập mẫu cho cả 5 horizon để có thể so sánh chỉ số công bằng.
    # Bỏ hàng bị ảnh hưởng bởi giờ trống, lag đầu chuỗi hoặc nhãn cuối chuỗi.
    valid = x.notna().all(axis=1) & y.notna().all(axis=1)
    x, y = x.loc[valid], y.loc[valid]

    # Học từ dữ liệu trước 2025, đánh giá trên 2025. Chừa đúng 48 giờ trước
    # ranh giới: nhãn xa nhất của mẫu train vẫn thuộc năm 2024.
    # Đặc trưng của test được phép nhìn lịch sử trước 2025, như khi dự báo thật.
    test_start = pd.Timestamp("2025-01-01")
    train = x.index < test_start - pd.Timedelta(hours=max(HORIZONS))
    test = x.index >= test_start
    results = []
    # Index ở đây là thời điểm dự đoán t; actual_h6 là giá trị thật tại t+6.
    predictions = pd.DataFrame(index=x.index[test])

    # Ridge của scikit-learn dự đoán một nhãn; lặp để fit 5 mô hình độc lập.
    for h in HORIZONS:
        column = f"h{h}"
        # Pipeline fit StandardScaler chỉ trên train, rồi Ridge học các cột
        # đã chuẩn hóa. Khi predict, scaler dùng lại thống kê của train.
        model = make_pipeline(StandardScaler(), Ridge(alpha=ALPHA))
        model.fit(x.loc[train], y.loc[train, column])
        predicted = model.predict(x.loc[test])
        actual = y.loc[test, column]

        # RMSE/MAE đo sai số theo µg/m³ (càng nhỏ càng tốt); R² càng cao càng tốt.
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
    # Làm tròn cho file báo cáo gọn hơn; việc fit và tính metric ở trên vẫn
    # dùng số thực đầy đủ, không làm tròn trước khi đánh giá.
    summary = pd.DataFrame(results).round(3)
    summary.to_csv(output / "metrics.csv", index=False)
    predictions.rename_axis("time").round(3).to_csv(output / "predictions.csv")
    print(summary.to_string(index=False))
    print(f"\nSaved results to: {output}")


if __name__ == "__main__":
    main()
