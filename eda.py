"""Thống kê và vẽ PM2.5 từ CSV đã tiền xử lý.

Chạy: python eda.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # lưu hình khi chạy trong terminal, không cần cửa sổ đồ họa
import matplotlib.pyplot as plt
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "hanoi_pm25_weather.csv"
OUTPUT = HERE / "output" / "eda"


def main():
    data = pd.read_csv(DATA, parse_dates=["time"]).set_index("time")
    pm = data["pm25"].dropna()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    summary = pm.describe(percentiles=[0.25, 0.5, 0.75, 0.95])
    by_year = pm.groupby(pm.index.year).agg(["count", "mean", "median"])
    by_month = pm.groupby(pm.index.month).mean()
    by_hour = pm.groupby(pm.index.hour).mean()
    correlation = data.corr(numeric_only=True)["pm25"].drop("pm25")
    missing = data.isna().sum()

    summary.rename_axis("statistic").to_csv(OUTPUT / "pm25_summary.csv", header=["value"])
    by_year.rename_axis("year").to_csv(OUTPUT / "pm25_by_year.csv")
    by_month.rename_axis("month").to_csv(OUTPUT / "pm25_by_month.csv", header=["mean_pm25"])
    by_hour.rename_axis("hour").to_csv(OUTPUT / "pm25_by_hour.csv", header=["mean_pm25"])
    correlation.rename_axis("weather").to_csv(OUTPUT / "weather_correlation.csv", header=["r_pm25"])
    missing.rename_axis("column").to_csv(OUTPUT / "missing_by_column.csv", header=["missing_hours"])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].hist(pm, bins=60, color="#4472c4")
    axes[0].set(title="PM2.5 distribution", xlabel="PM2.5 (µg/m³)", ylabel="Hours")
    axes[1].plot(by_month.index, by_month.values, marker="o", color="#c45a44")
    axes[1].set(title="Mean by month", xlabel="Month", ylabel="PM2.5 (µg/m³)", xticks=range(1, 13))
    axes[2].plot(by_hour.index, by_hour.values, color="#437c59")
    axes[2].set(title="Mean by hour", xlabel="Hour", ylabel="PM2.5 (µg/m³)", xticks=range(0, 24, 4))
    fig.tight_layout()
    fig.savefig(OUTPUT / "pm25_eda.png", dpi=180)
    plt.close(fig)

    print(f"PM2.5: {len(pm)} valid hours, mean {pm.mean():.2f} ug/m3")
    print(f"Saved EDA tables and chart to: {OUTPUT}")


if __name__ == "__main__":
    main()
