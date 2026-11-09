# Lời thuyết trình cho phần EDA

Thời lượng gợi ý: khoảng **2 phút**, chia thành ba slide. Số liệu lấy từ `data/hanoi_pm25_weather.csv` sau tiền xử lý và được tạo lại bằng `python eda.py`. Có thể dùng biểu đồ `output/eda/pm25_eda.png` cho phần phân bố, theo tháng và theo giờ.

## Slide 1 — Phân bố PM2.5

> Sau tiền xử lý, dữ liệu có 30.360 mốc giờ. Trong đó, 30.339 giờ có giá trị PM2.5 và 21 giờ vẫn còn thiếu. Nhìn vào biểu đồ phân bố, một nửa số giờ có PM2.5 từ 26 đến 61 microgam trên mét khối, nhưng vẫn có những thời điểm tăng rất cao. Trung bình là 50,72, lớn hơn trung vị 39,33; phân vị 95% đạt 130,33. Điều này cho thấy phân bố lệch về phía các giá trị cao. Vì vậy, khi đánh giá mô hình, nhóm sẽ xem cả MAE và RMSE; RMSE nhạy hơn với các sai số lớn.

**Số cần đặt trên slide:** `30.339/30.360 giờ hợp lệ` · `Trung vị 39,33` · `P95 130,33 µg/m³`.

## Slide 2 — Thay đổi theo tháng và giờ

> PM2.5 không giữ một mức cố định theo thời gian. Trong bộ dữ liệu này, trung bình theo tháng thấp nhất ở tháng 7, khoảng 24,63 microgam trên mét khối, và cao nhất ở tháng 11, khoảng 81,36. Trong ngày, mức trung bình thấp nhất vào khoảng 16 giờ và cao nhất khoảng 20 giờ. Những khác biệt này gợi ý rằng thời điểm trong ngày và trong năm có thể giúp dự đoán PM2.5, nên nhóm đưa đặc trưng lịch vào F4. Đây là trung bình mô tả dữ liệu; năm 2025 mới có sáu tháng đầu nên không thể so trực tiếp trung bình cả năm với các năm trước.

**Số cần đặt trên slide:** `Tháng 7: 24,63` · `Tháng 11: 81,36` · `16h: 40,72` · `20h: 57,59 µg/m³`.

## Slide 3 — PM2.5 và thời tiết

> Nhóm cũng xem tương quan giữa PM2.5 và các biến thời tiết. Áp suất có tương quan dương khoảng 0,35; nhiệt độ có tương quan âm khoảng 0,32; tốc độ gió có tương quan âm khoảng 0,17. Các hệ số này chỉ cho thấy hai biến thay đổi cùng nhau ở mức nào trong dữ liệu, không chứng minh quan hệ nguyên nhân. Dù vậy, chúng là cơ sở để thử đưa các quan trắc thời tiết vào bộ đặc trưng F4. Sang phần tiếp theo, nhóm sẽ trình bày cách Ridge dùng những đặc trưng này để dự đoán PM2.5 sau nhiều mốc giờ.

**Số cần đặt trên slide:** `Áp suất +0,346` · `Nhiệt độ −0,324` · `Gió −0,172` (tương quan Pearson với PM2.5).

## Lưu ý khi nói

- Phát âm đơn vị `µg/m³` là “microgam trên mét khối”.
- Slide 2 dùng trung bình của toàn bộ dữ liệu hiện có; đừng diễn giải thành quy luật chắc chắn cho mọi năm.
- Tương quan ở slide 3 là mô tả thống kê, không phải tác động nhân quả.
