# Dự đoán PM2.5 bằng Ridge (F4)

Bài thực hành Machine Learning áp dụng: dùng dữ liệu quan trắc theo giờ ở Hà Nội để dự đoán nồng độ PM2.5 sau **1, 6, 12, 24 và 48 giờ**. Dự án chỉ sử dụng **mô hình Ridge** và nhóm đặc trưng **F4**; mã và dữ liệu đều nằm trong thư mục AIL.

Xem [báo cáo quá trình thực hiện](REPORT.md) để đọc phần thu thập dữ liệu, tiền xử lý, EDA và kết quả dự đoán.

Nội dung thuyết trình phần thu thập dữ liệu: [slides/data_collection.md](slides/data_collection.md).

## Thu thập và tạo dataset

Yêu cầu Python 3.10 trở lên. Bốn CSV nguồn theo năm đã có sẵn trong `data/raw/`. Mở terminal trong thư mục `AIL` rồi chạy:

```bash
python -m pip install -r requirements.txt
python collect.py
python run.py
```

`collect.py` tạo lại `data/hanoi_pm25_weather.csv` hoàn toàn từ các CSV trong AIL. Nếu muốn tải lại dữ liệu gốc từ Kaggle, chạy `python collect.py --download` (cần mạng). Nguồn, phiên bản, mã SHA-256 và giải thích các cột nằm trong [data/SOURCE.md](data/SOURCE.md).

## Chạy mô hình

Chương trình in RMSE, MAE và R² theo từng mốc dự đoán. Hai tệp được tạo trong `output/`:

- `metrics.csv`: bảng chỉ số đánh giá.
- `predictions.csv`: giá trị thực và dự đoán cho từng thời điểm của tập kiểm tra.

## Dữ liệu và phương pháp

`data/hanoi_pm25_weather.csv` được tạo từ dữ liệu nguồn Kaggle [`phungdinhdat/aqi-in-hanoi-2022-2025`](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025). Dữ liệu từ 13/01/2022 đến 30/06/2025, mỗi hàng là một giờ. Tệp chỉ gồm thời gian, PM2.5 và 7 biến thời tiết: nhiệt độ (`temp`), độ ẩm (`rh`), tốc độ gió (`wind`), áp suất (`pressure`), lượng mưa (`precip`), mây (`clouds`), chỉ số UV (`uv`). Các ô trống là giờ thiếu dữ liệu, được giữ để không làm lệch các khoảng trễ.

F4 sử dụng PM2.5 hiện tại và quá khứ, thống kê trên các cửa sổ thời gian, đặc trưng lịch và thời tiết hiện tại/quá khứ. Mỗi mốc thời gian có một mô hình Ridge riêng. Dữ liệu đến hết năm 2024 dùng để huấn luyện; nửa đầu năm 2025 dùng để kiểm tra. Chương trình chừa 48 giờ ở ranh giới để nhãn huấn luyện không lấy giá trị thuộc tập kiểm tra. Việc chuẩn hóa đặc trưng được học **chỉ trên tập huấn luyện**. Hệ số điều chuẩn `alpha = 1554.6367` được cố định cho bài thực hành này.

**Cách đọc kết quả:** RMSE và MAE càng thấp càng tốt; R² càng cao càng tốt. Đây là dự đoán từ thông tin quan trắc có tại thời điểm dự đoán, gồm cả thời tiết tại thời điểm đó.

## Cấu trúc

```text
AIL/
├── data/raw/2022.csv ... 2025.csv # dữ liệu nguồn theo năm
├── data/hanoi_pm25_weather.csv    # dữ liệu dùng cho mô hình
├── data/SOURCE.md                 # nguồn và mô tả dữ liệu
├── collect.py                     # thu thập và tạo dataset
├── run.py                         # tạo đặc trưng, huấn luyện, đánh giá
├── REPORT.md                      # báo cáo quá trình thực hiện
├── requirements.txt
└── output/                        # được tạo khi chạy
```
