"""Tạo dữ liệu PM2.5 + thời tiết từ bốn CSV gốc.

python collect.py             # dùng data/raw/*.csv đi kèm dự án
python collect.py --download  # tải lại bản nguồn từ Kaggle trước khi xử lý
"""

import argparse
import shutil
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
OUTPUT = HERE / "data" / "hanoi_pm25_weather.csv"
YEARS = [2022, 2023, 2024, 2025]
SOURCE = "phungdinhdat/aqi-in-hanoi-2022-2025/versions/1"
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


def download_raw():
    """Lưu bản CSV nguồn theo năm vào chính thư mục AIL."""
    import kagglehub

    source_dir = Path(kagglehub.dataset_download(SOURCE))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        shutil.copy2(source_dir / f"{year}.csv", RAW_DIR / f"{year}.csv")


def build_dataset():
    """Chọn cột F4, khôi phục trục giờ và xử lý khoảng trống ngắn."""
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Thiếu CSV nguồn: {missing}. Chạy python collect.py --download")

    parts = [pd.read_csv(path, usecols=list(COLUMNS)) for path in files]
    data = pd.concat(parts, ignore_index=True).rename(columns=COLUMNS)
    data["time"] = pd.to_datetime(data["time"])
    data = data.sort_values("time").drop_duplicates("time", keep="last")
    data = data.set_index("time")
    data = data[list(COLUMNS.values())[1:]]

    # Một hàng luôn tương ứng một giờ; giữ các khoảng trống dài dưới dạng NaN.
    hours = pd.date_range(data.index.min(), data.index.max(), freq="h", name="time")
    data = data.reindex(hours)
    data = data.interpolate(limit=3, limit_area="inside")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT, date_format="%Y-%m-%d %H:%M:%S", lineterminator="\n")
    print(f"Created {OUTPUT.name}: {len(data)} hourly rows, {data.pm25.isna().sum()} missing PM2.5 hours")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Tải lại bốn CSV từ Kaggle")
    args = parser.parse_args()
    if args.download:
        download_raw()
    build_dataset()
