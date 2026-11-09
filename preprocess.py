"""Tạo CSV dùng cho mô hình từ bốn CSV nguồn trong AIL.

Chạy: python preprocess.py
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
OUTPUT = HERE / "data" / "hanoi_pm25_weather.csv"
YEARS = [2022, 2023, 2024, 2025]
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
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing raw CSV: {missing}. Run python collect.py --download")

    parts = [pd.read_csv(path, usecols=list(COLUMNS)) for path in files]
    data = pd.concat(parts, ignore_index=True).rename(columns=COLUMNS)
    data["time"] = pd.to_datetime(data["time"])
    data = data.sort_values("time").drop_duplicates("time", keep="last")
    data = data.set_index("time")
    data = data[list(COLUMNS.values())[1:]]

    # Khôi phục các giờ trống để lag 24 luôn có nghĩa là 24 giờ trước.
    hours = pd.date_range(data.index.min(), data.index.max(), freq="h", name="time")
    data = data.reindex(hours)
    data = data.interpolate(limit=3, limit_area="inside")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT, date_format="%Y-%m-%d %H:%M:%S", lineterminator="\n")
    print(f"Created {OUTPUT.name}: {len(data)} hourly rows, {data.pm25.isna().sum()} missing PM2.5 hours")


if __name__ == "__main__":
    main()
