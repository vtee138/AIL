"""Bước 1: gộp và chọn cột từ CSV nguồn, chưa tiền xử lý.

python collect.py             # tạo data/collected_pm25_weather.csv
python collect.py --download  # tải lại phiên bản nguồn từ Kaggle

Bốn tệp data/raw/{năm}.csv được giữ nguyên. CSV mới chỉ chọn 9 cột gốc;
giữ nguyên thứ tự hàng, tên cột, giá trị trống và bản ghi trùng.
"""

import argparse
import csv
import shutil
from pathlib import Path

# Dùng vị trí của file Python thay vì thư mục đang mở trong terminal. Nhờ đó,
# `python AIL/collect.py` vẫn tìm đúng dữ liệu dù chạy từ thư mục khác.
HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
OUTPUT = HERE / "data" / "collected_pm25_weather.csv"
YEARS = [2022, 2023, 2024, 2025]
# Ghim phiên bản 1 để lần tải sau không vô tình lấy một phiên bản dữ liệu mới.
SOURCE = "phungdinhdat/aqi-in-hanoi-2022-2025/versions/1"
# Tên cột ở đây vẫn là tên gốc trong CSV Kaggle. Đổi tên là việc của preprocess.py.
KEEP_COLUMNS = [
    "Local Time", "PM25", "Temperature", "Relative Humidity", "Wind Speed",
    "Pressure", "Precipitation", "Clouds", "UV Index",
]


def download_raw():
    """Tải bộ dữ liệu công khai và chép nguyên các CSV gốc vào AIL."""
    import kagglehub

    # kagglehub có thể trả về thư mục cache; copy2 đưa dữ liệu vào chính dự án.
    source_dir = Path(kagglehub.dataset_download(SOURCE))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        shutil.copy2(source_dir / f"{year}.csv", RAW_DIR / f"{year}.csv")


def collect_dataset():
    """Gộp bốn CSV theo thứ tự năm và sao chép nguyên giá trị của 9 cột."""
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Thiếu CSV nguồn: {missing}. Chạy python collect.py --download")

    # csv.DictReader/DictWriter giữ giá trị dưới dạng chuỗi, không tự nội suy,
    # sắp xếp hoặc loại trùng. Bước này chỉ chọn cột và gộp hàng.
    with OUTPUT.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=KEEP_COLUMNS, lineterminator="\n")
        writer.writeheader()
        total = 0
        for path in files:
            with path.open(encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                absent = set(KEEP_COLUMNS) - set(reader.fieldnames or [])
                if absent:
                    raise ValueError(f"{path.name} thiếu cột: {sorted(absent)}")
                count = 0
                for row in reader:
                    writer.writerow({name: row[name] for name in KEEP_COLUMNS})
                    count += 1
            total += count
            print(f"{path.name}: {count} rows")
    print(f"Created {OUTPUT.name}: {total} raw rows, {len(KEEP_COLUMNS)} columns")


if __name__ == "__main__":
    # Mặc định dùng CSV đã có sẵn. Chỉ tải từ mạng khi người chạy thêm --download.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Tải lại bốn CSV từ Kaggle")
    args = parser.parse_args()
    if args.download:
        download_raw()
    collect_dataset()
