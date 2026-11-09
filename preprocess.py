"""Bước 2: tạo một bảng theo giờ cho bài toán dự đoán PM2.5.

Chạy: python preprocess.py

Đầu vào: data/raw/2022.csv ... data/raw/2025.csv.
Đầu ra: data/hanoi_pm25_weather.csv, gồm time, pm25 và 7 biến thời tiết.
Script chỉ xử lý dữ liệu; nó không huấn luyện mô hình.
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
OUTPUT = HERE / "data" / "hanoi_pm25_weather.csv"
YEARS = [2022, 2023, 2024, 2025]
# Khóa là tên cột trong dữ liệu Kaggle, giá trị là tên ngắn dùng trong AIL.
# Chỉ chọn PM2.5 và thời tiết vì F4 không dùng các chất ô nhiễm khác.
COLUMNS = {
    "Local Time": "time",
    "PM25": "pm25",
    "Temperature": "temp",
    "Relative Humidity": "rh",
    "Wind Speed": "wind",
    "Pressure": "pressure",
    "Precipitation": "precip",
    "Clouds": "clouds",
    "UV Index": "uv",
}


def main():
    """Gộp CSV, giữ một hàng mỗi giờ, nội suy ngắn rồi lưu bảng sạch."""
    # Dừng sớm với thông báo rõ ràng nếu chưa có đủ dữ liệu nguồn.
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing raw CSV: {missing}. Run python collect.py --download")

    # usecols tránh nạp các cột không cần như AQI hay các chất ô nhiễm khác.
    parts = [pd.read_csv(path, usecols=list(COLUMNS)) for path in files]
    data = pd.concat(parts, ignore_index=True).rename(columns=COLUMNS)
    # Local Time là giờ địa phương của Hà Nội. Dùng nó làm chỉ số thời gian.
    data["time"] = pd.to_datetime(data["time"])
    # Nếu một giờ xuất hiện nhiều lần, giữ bản ghi cuối cùng của giờ đó.
    data = data.sort_values("time").drop_duplicates("time", keep="last")
    data = data.set_index("time")
    # Cố định thứ tự cột để CSV tạo lại luôn có cùng cấu trúc.
    data = data[list(COLUMNS.values())[1:]]

    # Khôi phục các giờ trống: sau bước này, dịch 24 hàng sẽ đúng là 24 giờ.
    # Ví dụ, ngày 31/12/2023 thiếu trong nguồn nhưng vẫn có vị trí trên trục giờ.
    hours = pd.date_range(data.index.min(), data.index.max(), freq="h", name="time")
    data = data.reindex(hours)
    # Chỉ lấp tối đa 3 ô trống liên tiếp từ dữ liệu hai phía. Khoảng trống dài
    # vẫn còn NaN; model.py sẽ bỏ những mẫu có đặc trưng/nhãn chạm NaN đó.
    data = data.interpolate(limit=3, limit_area="inside")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    # Xuống dòng LF giúp CSV tái tạo nhất quán trên Windows và các hệ điều hành khác.
    data.to_csv(OUTPUT, date_format="%Y-%m-%d %H:%M:%S", lineterminator="\n")
    print(f"Created {OUTPUT.name}: {len(data)} hourly rows, {data.pm25.isna().sum()} missing PM2.5 hours")


if __name__ == "__main__":
    main()
