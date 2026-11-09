"""Bước 1: thu thập dữ liệu nguồn, chưa làm sạch hay tạo đặc trưng.

python collect.py             # kiểm tra các CSV có sẵn
python collect.py --download  # tải lại phiên bản nguồn từ Kaggle

Đầu ra của bước này là bốn tệp data/raw/{năm}.csv. Các bước sau chỉ đọc
những tệp này, nên có thể chạy lại dự án khi không có kết nối mạng.
"""

import argparse
import shutil
from pathlib import Path

# Dùng vị trí của file Python thay vì thư mục đang mở trong terminal. Nhờ đó,
# `python AIL/collect.py` vẫn tìm đúng dữ liệu dù chạy từ thư mục khác.
HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
YEARS = [2022, 2023, 2024, 2025]
# Ghim phiên bản 1 để lần tải sau không vô tình lấy một phiên bản dữ liệu mới.
SOURCE = "phungdinhdat/aqi-in-hanoi-2022-2025/versions/1"


def download_raw():
    """Tải bộ dữ liệu công khai và chép nguyên các CSV gốc vào AIL."""
    import kagglehub

    # kagglehub có thể trả về thư mục cache; copy2 đưa dữ liệu vào chính dự án.
    source_dir = Path(kagglehub.dataset_download(SOURCE))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        shutil.copy2(source_dir / f"{year}.csv", RAW_DIR / f"{year}.csv")


def check_raw():
    """Báo số hàng của từng CSV để xác nhận đã thu thập đủ bốn năm."""
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Thiếu CSV nguồn: {missing}. Chạy python collect.py --download")
    for path in files:
        # Mỗi bản ghi nằm trên một dòng; dòng đầu là tên cột, không phải dữ liệu.
        with path.open(encoding="utf-8") as file:
            rows = sum(1 for _ in file) - 1  # trừ hàng tiêu đề
        print(f"{path.name}: {rows} rows")


if __name__ == "__main__":
    # Mặc định dùng CSV đã có sẵn. Chỉ tải từ mạng khi người chạy thêm --download.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Tải lại bốn CSV từ Kaggle")
    args = parser.parse_args()
    if args.download:
        download_raw()
    check_raw()
