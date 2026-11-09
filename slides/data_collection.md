# Data Collection — nội dung để đưa vào slide

## Slide 1 — Nguồn dữ liệu

**Tiêu đề:** Dữ liệu quan trắc chất lượng không khí Hà Nội

**Nội dung trên slide**

- Nguồn: bộ *AQI in Hanoi 2022–2025* trên Kaggle, phiên bản 1.
- Phạm vi: Hà Nội, từ **13/01/2022** đến **30/06/2025**; dữ liệu theo giờ.
- **4 tệp CSV** theo năm, tổng cộng **30.341 bản ghi gốc**.
- Lưu nguyên các tệp nguồn trong `data/raw/` để có thể kiểm tra và tạo lại dataset.

**Lời trình bày (khoảng 25 giây)**

> Nhóm sử dụng một bộ dữ liệu công khai về chất lượng không khí tại Hà Nội. Dữ liệu được chia thành bốn tệp theo năm, từ 2022 đến nửa đầu 2025. Chúng tôi giữ bản CSV gốc trong dự án để quá trình xử lý có thể tái hiện.

**Nguồn ghi ở chân slide:** [Kaggle — AQI in Hanoi 2022–2025](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025), `phungdinhdat`, phiên bản 1.

## Slide 2 — CSV sau Data Collection

**Tiêu đề:** Chọn cột cho bài toán PM2.5

**Nội dung trên slide**

- **Biến mục tiêu:** PM2.5 (µg/m³).
- **Thông tin đầu vào:** thời gian quan trắc; nhiệt độ, độ ẩm, gió, áp suất, mưa, mây và UV.
- `collect.py` tạo `data/collected_pm25_weather.csv`: **30.341 hàng, 9 cột tên gốc**.
- CSV này **chưa xử lý** giờ trùng, giờ thiếu hay đổi tên cột. Đó là việc của phần *Tiền xử lý*.

**Lời trình bày (khoảng 30 giây)**

> Mục tiêu của bài là dự đoán nồng độ PM2.5. Vì dùng bộ đặc trưng F4, nhóm chỉ giữ thời gian, PM2.5 và bảy chỉ số thời tiết; các chất ô nhiễm khác trong nguồn gốc không được đưa vào mô hình. CSV của bước thu thập vẫn giữ dữ liệu thô của những cột này. Phần tiếp theo mới xử lý bản ghi trùng và khoảng thời gian bị thiếu.

**Gợi ý minh họa:** `4 CSV gốc → collect.py → collected_pm25_weather.csv (30.341 hàng, chưa làm sạch)`.
