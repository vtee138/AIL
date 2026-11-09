# Nguồn dữ liệu AIL

- Nguồn: [AQI in Hanoi 2022–2025 trên Kaggle](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025), tác giả `phungdinhdat`.
- Bản dữ liệu: `versions/1`.
- Các tệp gốc được lưu nguyên trong `raw/2022.csv`, `raw/2023.csv`, `raw/2024.csv`, `raw/2025.csv`.
- `python collect.py` chọn 9 cột từ bốn CSV gốc và gộp thành `collected_pm25_weather.csv` (30.341 hàng). Tên cột, giá trị trống, hàng trùng và thứ tự hàng gốc vẫn được giữ. `python collect.py --download` tải lại đúng phiên bản nguồn từ Kaggle trước khi tạo CSV (cần mạng).
- `python preprocess.py` chỉ đọc `collected_pm25_weather.csv`, đổi tên cột, loại giờ trùng, tạo trục giờ liên tục và nội suy tối đa 3 giờ. Đầu ra là `hanoi_pm25_weather.csv` (30.360 mốc giờ). Đây là CSV dùng cho EDA và mô hình.

## Kiểm tra tệp nguồn

SHA-256 của bốn tệp CSV được lưu cùng dự án:

```text
fe08e2d57a5109722c1e174c976a770583d386ff77f13ffdef6b0815e355405b  2022.csv
0c1d984ccac322e32497fe18524106a6f4135d410229b88ca0fd5a0f112024f8  2023.csv
f9acf515dda02fba3b34e671cc4ebddd555e5bf898d6bcbd22d30726bf845032  2024.csv
6f2b2290667fc17daf1fa08592909122c815c8051c8a7352e77f8d3192983999  2025.csv
```

Tên cột trong hai CSV của hai giai đoạn:

| Data Collection | Preprocessing | Ý nghĩa |
|---|---|---|
| `Local Time` | `time` | Giờ địa phương của Hà Nội |
| `PM25` | `pm25` | Nồng độ PM2.5, biến mục tiêu |
| `Temperature` | `temp` | Nhiệt độ |
| `Relative Humidity` | `rh` | Độ ẩm tương đối |
| `Wind Speed` | `wind` | Tốc độ gió |
| `Pressure` | `pressure` | Áp suất |
| `Precipitation` | `precip` | Lượng mưa |
| `Clouds` | `clouds` | Mây |
| `UV Index` | `uv` | Chỉ số UV |
