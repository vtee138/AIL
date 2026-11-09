# Nguồn dữ liệu AIL

- Nguồn: [AQI in Hanoi 2022–2025 trên Kaggle](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025), tác giả `phungdinhdat`.
- Bản dữ liệu: `versions/1`.
- Các tệp gốc được lưu nguyên trong `raw/2022.csv`, `raw/2023.csv`, `raw/2024.csv`, `raw/2025.csv`.
- `hanoi_pm25_weather.csv` được tạo từ bốn tệp gốc bằng `python collect.py` ở thư mục AIL. Script chỉ chọn các cột cần cho bài Ridge F4, loại giờ trùng, tạo trục giờ liên tục và nội suy tối đa 3 giờ.
- `python collect.py --download` tải lại đúng phiên bản nguồn từ Kaggle trước khi tạo CSV. Lệnh này cần kết nối mạng; chạy `python collect.py` với các CSV gốc có sẵn thì không cần mạng.

## Kiểm tra tệp nguồn

SHA-256 của bốn tệp CSV được lưu cùng dự án:

```text
fe08e2d57a5109722c1e174c976a770583d386ff77f13ffdef6b0815e355405b  2022.csv
0c1d984ccac322e32497fe18524106a6f4135d410229b88ca0fd5a0f112024f8  2023.csv
f9acf515dda02fba3b34e671cc4ebddd555e5bf898d6bcbd22d30726bf845032  2024.csv
6f2b2290667fc17daf1fa08592909122c815c8051c8a7352e77f8d3192983999  2025.csv
```

Tên cột của tệp dùng cho mô hình:

| Cột | Ý nghĩa |
|---|---|
| `time` | Giờ địa phương của Hà Nội |
| `pm25` | Nồng độ PM2.5, biến mục tiêu |
| `temp` | Nhiệt độ |
| `rh` | Độ ẩm tương đối |
| `wind` | Tốc độ gió |
| `pressure` | Áp suất |
| `precip` | Lượng mưa |
| `clouds` | Mây |
| `uv` | Chỉ số UV |
