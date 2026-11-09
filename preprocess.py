"""Bước 2: tiền xử lý CSV đã chọn cột ở bước Data Collection.

Chạy: python preprocess.py

Đầu vào: data/collected_pm25_weather.csv do collect.py tạo.
Đầu ra: data/hanoi_pm25_weather.csv, gồm time, pm25 và 7 biến thời tiết.
Script chỉ xử lý dữ liệu; nó không huấn luyện mô hình.
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
INPUT = HERE / "data" / "collected_pm25_weather.csv"
OUTPUT = HERE / "data" / "hanoi_pm25_weather.csv"
# Việc chọn cột đã hoàn tất ở collect.py; ở đây chỉ chuẩn hóa tên cột.
# Khóa là tên gốc, giá trị là tên ngắn dùng trong EDA và mô hình.
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
    """Đổi tên, giữ một hàng mỗi giờ, nội suy ngắn rồi lưu bảng sạch."""
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing {INPUT.name}. Run python collect.py first")

    # CSV đầu vào vẫn có tên cột gốc, hàng trùng và khoảng giờ bị thiếu.
    data = pd.read_csv(INPUT).rename(columns=COLUMNS)
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
