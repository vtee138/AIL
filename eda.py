"""Bước 3: khám phá dữ liệu (EDA) trước khi đọc kết quả mô hình.

Chạy: python eda.py

Đọc data/hanoi_pm25_weather.csv và lưu bảng/biểu đồ vào output/eda/.
Các thống kê ở đây mô tả dữ liệu, không được đưa vào bước fit mô hình.
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
    """Tính phân bố, xu hướng theo lịch, tương quan và số ô còn thiếu."""
    # parse_dates chuyển chuỗi thời gian thành kiểu datetime để nhóm theo năm,
    # tháng và giờ. Mỗi hàng của CSV tương ứng một mốc giờ.
    data = pd.read_csv(DATA, parse_dates=["time"]).set_index("time")
    # Các phép thống kê PM2.5 chỉ dùng giờ có giá trị quan trắc/nội suy hợp lệ.
    pm = data["pm25"].dropna()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # describe cho biết trung bình, độ lệch chuẩn và các phân vị. Nhóm theo năm,
    # tháng, giờ để xem PM2.5 thay đổi theo thời gian. Năm 2025 chỉ có 6 tháng.
    summary = pm.describe(percentiles=[0.25, 0.5, 0.75, 0.95])
    by_year = pm.groupby(pm.index.year).agg(["count", "mean", "median"])
    by_month = pm.groupby(pm.index.month).mean()
    by_hour = pm.groupby(pm.index.hour).mean()
    # Hệ số Pearson chỉ mô tả mức liên hệ tuyến tính, không chứng minh nguyên nhân.
    correlation = data.corr(numeric_only=True)["pm25"].drop("pm25")
    # Đếm NaN ở từng cột để biết bao nhiêu giờ vẫn thiếu sau tiền xử lý.
    missing = data.isna().sum()

    # Lưu số liệu dưới dạng CSV để dễ kiểm tra hoặc đưa vào bảng thuyết trình.
    summary.rename_axis("statistic").to_csv(OUTPUT / "pm25_summary.csv", header=["value"])
    by_year.rename_axis("year").to_csv(OUTPUT / "pm25_by_year.csv")
    by_month.rename_axis("month").to_csv(OUTPUT / "pm25_by_month.csv", header=["mean_pm25"])
    by_hour.rename_axis("hour").to_csv(OUTPUT / "pm25_by_hour.csv", header=["mean_pm25"])
    correlation.rename_axis("weather").to_csv(OUTPUT / "weather_correlation.csv", header=["r_pm25"])
    missing.rename_axis("column").to_csv(OUTPUT / "missing_by_column.csv", header=["missing_hours"])

    # Hình 1: phân bố nồng độ. Hình 2-3: trung bình theo tháng và giờ trong ngày.
    # Các đường này là mô tả tổng hợp, không phải dự đoán của mô hình.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].hist(pm, bins=60, color="#4472c4")
    axes[0].set(title="PM2.5 distribution", xlabel="PM2.5 (µg/m³)", ylabel="Hours")
    axes[1].plot(by_month.index, by_month.values, marker="o", color="#c45a44")
    axes[1].set(title="Mean by month", xlabel="Month", ylabel="PM2.5 (µg/m³)", xticks=range(1, 13))
    axes[2].plot(by_hour.index, by_hour.values, color="#437c59")
    axes[2].set(title="Mean by hour", xlabel="Hour", ylabel="PM2.5 (µg/m³)", xticks=range(0, 24, 4))
    fig.tight_layout()
    fig.savefig(OUTPUT / "pm25_eda.png", dpi=180)
    plt.close(fig)  # giải phóng bộ nhớ sau khi lưu ảnh

    print(f"PM2.5: {len(pm)} valid hours, mean {pm.mean():.2f} ug/m3")
    print(f"Saved EDA tables and chart to: {OUTPUT}")


if __name__ == "__main__":
    main()
