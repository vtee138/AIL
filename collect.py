"""Kiểm tra hoặc tải bốn CSV nguồn về thư mục AIL.

python collect.py             # kiểm tra các CSV có sẵn
python collect.py --download  # tải lại phiên bản nguồn từ Kaggle
"""

import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
YEARS = [2022, 2023, 2024, 2025]
SOURCE = "phungdinhdat/aqi-in-hanoi-2022-2025/versions/1"


def download_raw():
    """Lưu bản CSV nguồn theo năm vào chính thư mục AIL."""
    import kagglehub

    source_dir = Path(kagglehub.dataset_download(SOURCE))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        shutil.copy2(source_dir / f"{year}.csv", RAW_DIR / f"{year}.csv")


def check_raw():
    """Báo số hàng của các tệp nguồn, chưa thay đổi dữ liệu."""
    files = [RAW_DIR / f"{year}.csv" for year in YEARS]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Thiếu CSV nguồn: {missing}. Chạy python collect.py --download")
    for path in files:
        with path.open(encoding="utf-8") as file:
            rows = sum(1 for _ in file) - 1  # trừ hàng tiêu đề
        print(f"{path.name}: {rows} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Tải lại bốn CSV từ Kaggle")
    args = parser.parse_args()
    if args.download:
        download_raw()
    check_raw()
