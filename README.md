# Dự đoán PM2.5 bằng Ridge (F4)

Bài thực hành Machine Learning áp dụng: dùng dữ liệu quan trắc theo giờ ở Hà Nội để dự đoán nồng độ PM2.5 sau **1, 6, 12, 24 và 48 giờ**. Đây là bản tách độc lập từ dự án DAP, chỉ giữ một mô hình **Ridge** và một nhóm đặc trưng **F4**.

Xem [báo cáo quá trình thực hiện](REPORT.md) để đọc phần thu thập dữ liệu, tiền xử lý, EDA và kết quả dự đoán.

## Chạy chương trình

Yêu cầu Python 3.10 trở lên. Mở terminal trong thư mục `AIL` rồi chạy:

```bash
python -m pip install -r requirements.txt
python run.py
```

Chương trình in RMSE, MAE và R² theo từng mốc dự đoán. Hai tệp được tạo trong `output/`:

- `metrics.csv`: bảng chỉ số đánh giá.
- `predictions.csv`: giá trị thực và dự đoán cho từng thời điểm của tập kiểm tra.

## Dữ liệu và phương pháp

`data/hanoi_pm25_weather.csv` là bộ dữ liệu riêng của AIL, trích từ dữ liệu đã làm sạch trong DAP. Nguồn ban đầu: Kaggle [`phungdinhdat/aqi-in-hanoi-2022-2025`](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025). Dữ liệu từ 13/01/2022 đến 30/06/2025, mỗi hàng là một giờ. Tệp chỉ gồm thời gian, PM2.5 và 7 biến thời tiết: nhiệt độ (`temp`), độ ẩm (`rh`), tốc độ gió (`wind`), áp suất (`pressure`), lượng mưa (`precip`), mây (`clouds`), chỉ số UV (`uv`). Các ô trống là giờ thiếu dữ liệu, được giữ để không làm lệch các khoảng trễ.

F4 sử dụng PM2.5 hiện tại và quá khứ, thống kê trên các cửa sổ thời gian, đặc trưng lịch và thời tiết hiện tại/quá khứ. Mỗi mốc thời gian có một mô hình Ridge riêng. Dữ liệu đến hết năm 2024 dùng để huấn luyện; nửa đầu năm 2025 dùng để kiểm tra. Chương trình chừa 48 giờ ở ranh giới để nhãn huấn luyện không lấy giá trị thuộc tập kiểm tra. Việc chuẩn hóa đặc trưng được học **chỉ trên tập huấn luyện**. `alpha = 1554.6367` là giá trị đã chọn trong DAP, không tối ưu lại trên tập kiểm tra.

**Cách đọc kết quả:** RMSE và MAE càng thấp càng tốt; R² càng cao càng tốt. Đây là dự đoán từ thông tin quan trắc có tại thời điểm dự đoán, gồm cả thời tiết tại thời điểm đó. Kết quả có thể hơi khác báo cáo DAP vì bản này loại các nhãn vượt qua ranh giới huấn luyện/kiểm tra.

## Cấu trúc

```text
AIL/
├── data/hanoi_pm25_weather.csv   # dữ liệu độc lập
├── run.py                        # tạo đặc trưng, huấn luyện, đánh giá
├── requirements.txt
└── output/                       # được tạo khi chạy
```
