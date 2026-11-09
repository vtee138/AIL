# Báo cáo quá trình thực hiện dự án

## Dự đoán PM2.5 tại Hà Nội bằng Ridge Regression

**Mục tiêu.** Từ các quan trắc có tại một thời điểm, dự đoán nồng độ PM2.5 sau 1, 6, 12, 24 và 48 giờ. Đây là bài thực hành Machine Learning áp dụng dành cho thuyết trình sinh viên, chỉ sử dụng **mô hình Ridge với bộ đặc trưng F4**.

Quy trình gồm bốn bước: **thu thập dữ liệu → tiền xử lý → khám phá dữ liệu (EDA) → dự đoán và đánh giá**.

## 1. Data collection — Thu thập dữ liệu

Nguồn là bộ [AQI in Hanoi 2022–2025 trên Kaggle](https://www.kaggle.com/datasets/phungdinhdat/aqi-in-hanoi-2022-2025), phiên bản 1, gồm bốn tệp CSV theo năm. AIL lưu nguyên các tệp tại `data/raw/2022.csv` đến `data/raw/2025.csv`. `collect.py` kiểm tra tệp nguồn hoặc tải lại từ Kaggle; `preprocess.py` tạo `data/hanoi_pm25_weather.csv` với các cột cần cho F4. Mã SHA-256 và mô tả từng cột nằm trong `data/SOURCE.md`.

| Thành phần | Nội dung |
|---|---|
| Địa điểm | Hà Nội |
| Độ phân giải | 1 hàng mỗi giờ, theo giờ địa phương |
| Khoảng thời gian | 13/01/2022 00:00 đến 30/06/2025 23:00 |
| Quy mô sau khi đưa về trục giờ liên tục | 30.360 hàng |
| Biến cần dự đoán | `pm25` — nồng độ PM2.5 (µg/m³) |
| Biến thời tiết | `temp`, `rh`, `wind`, `pressure`, `precip`, `clouds`, `uv` |

Tệp dữ liệu AIL có 9 cột: `time`, `pm25` và 7 biến thời tiết. Các chất ô nhiễm khác, AQI và thông tin địa danh không được đưa vào mô hình này.

## 2. Tiền xử lý dữ liệu

1. **Chuẩn hóa cấu trúc:** `preprocess.py` đổi tên các cột cần dùng sang tên ngắn, chuyển `Local Time` thành thời gian, sắp xếp theo thời gian và loại các bản ghi trùng giờ. Dữ liệu nguồn có 5 bản ghi trùng thời gian; tệp dùng cho mô hình không còn giờ trùng.
2. **Tạo trục giờ liên tục:** Một khoảng thiếu 24 giờ vào ngày 31/12/2023 được giữ đúng vị trí trên trục thời gian. Nhờ đó, phép tạo độ trễ theo hàng vẫn tương ứng với số giờ thực tế.
3. **Xử lý giá trị thiếu:** `preprocess.py` nội suy tối đa 3 giờ liên tiếp và giữ các giờ còn thiếu dưới dạng ô trống. Trong tệp dùng cho mô hình còn 21 giờ thiếu ở ngày 31/12/2023, ở cả PM2.5 và các biến thời tiết. Khi tạo dữ liệu học, các hàng có đặc trưng hoặc nhãn thiếu được loại bỏ.
4. **Tạo đặc trưng F4:** Từ PM2.5 và thời tiết, tạo giá trị tại thời điểm hiện tại, các độ trễ và thống kê cửa sổ; bổ sung đặc trưng giờ, thứ, ngày trong năm, cuối tuần và ngày lễ Việt Nam. Tất cả đặc trưng của hàng thời điểm `t` chỉ dùng dữ liệu tại `t` hoặc trước `t`.
5. **Chuẩn hóa thang đo:** `StandardScaler` được đặt trong pipeline cùng Ridge. Bộ chuẩn hóa được `fit` trên tập huấn luyện rồi áp dụng cho tập kiểm tra, tránh dùng thống kê của tập kiểm tra khi huấn luyện.

F4 có **150 đặc trưng**: 44 từ PM2.5, 8 từ lịch và 98 từ 7 biến thời tiết. Một số đặc trưng có ý nghĩa trực quan là PM2.5 hiện tại, PM2.5 cách 24 giờ, trung bình PM2.5 trong 6 giờ gần nhất và nhiệt độ tại thời điểm dự đoán.

## 3. EDA — Khám phá dữ liệu

Các thống kê dưới đây tính trên `data/hanoi_pm25_weather.csv` sau bước làm sạch và trước khi tạo đặc trưng. Số lượng quan sát PM2.5 hợp lệ là **30.339/30.360 giờ**.

### 3.1. Phân bố PM2.5

| Chỉ số | Giá trị (µg/m³) |
|---|---:|
| Trung bình | 50,72 |
| Trung vị | 39,33 |
| Độ lệch chuẩn | 40,64 |
| Phân vị 25% / 75% | 26,00 / 61,00 |
| Phân vị 95% | 130,33 |
| Nhỏ nhất / lớn nhất | 1,00 / 457,00 |

Trung bình cao hơn trung vị và phân vị 95% cao hơn nhiều so với trung vị: phân bố có đuôi phải, tức có những giờ ô nhiễm tăng mạnh. Vì thế, chỉ nhìn sai số trung bình sẽ chưa mô tả hết các trường hợp khó dự đoán.

### 3.2. Thay đổi theo thời gian

| Năm | Số giờ PM2.5 hợp lệ | PM2.5 trung bình (µg/m³) |
|---|---:|---:|
| 2022 | 8.472 | 48,15 |
| 2023 | 8.739 | 52,48 |
| 2024 | 8.784 | 46,21 |
| 2025, tháng 1–6 | 4.344 | 61,30 |

Nửa đầu 2025 có PM2.5 trung bình cao hơn nửa đầu 2022 (53,52), 2023 (48,99) và 2024 (42,65 µg/m³). Năm 2025 chỉ có dữ liệu đến hết tháng 6 nên không nên so trực tiếp với **trung bình cả năm** của những năm trước.

Theo tháng, trung bình PM2.5 thấp nhất ở tháng 7 (**24,63 µg/m³**) và cao nhất ở tháng 11 (**81,36 µg/m³**) trong khoảng dữ liệu hiện có. Theo giờ trong ngày, mức trung bình thấp nhất khoảng 16:00 (**40,72 µg/m³**) và cao nhất khoảng 20:00 (**57,59 µg/m³**). Các mẫu hình này là lý do hợp lý để đưa đặc trưng lịch vào F4; chúng không chứng minh quan hệ nhân quả.

### 3.3. Liên hệ với thời tiết

Tương quan Pearson giữa PM2.5 và một số biến thời tiết trong toàn bộ tệp: áp suất **+0,346**, nhiệt độ **−0,324**, tốc độ gió **−0,172**, lượng mưa **−0,099**. Đây là tương quan đơn biến, có thể chịu ảnh hưởng của mùa và những yếu tố khác; chúng không có nghĩa là thay đổi một biến thời tiết sẽ gây ra đúng mức thay đổi PM2.5 tương ứng.

## 4. Predict — Huấn luyện và dự đoán

### 4.1. Bài toán và cách chia dữ liệu

Tại mỗi thời điểm `t`, chương trình tạo 5 nhãn: PM2.5 tại `t+1`, `t+6`, `t+12`, `t+24` và `t+48` giờ. Mỗi mốc có **một mô hình Ridge riêng**. Các hàng chỉ được giữ khi đủ 150 đặc trưng và cả 5 nhãn.

| Tập | Khoảng thời điểm đầu vào | Số mẫu |
|---|---|---:|
| Huấn luyện | 20/01/2022 00:00 – 29/12/2024 23:00 | 25.647 |
| Đệm ranh giới | 30–31/12/2024 | 48 |
| Kiểm tra | 01/01/2025 00:00 – 28/06/2025 23:00 | 4.296 |

Khoảng đệm 48 giờ bảo đảm nhãn `t+48` của tập huấn luyện vẫn nằm trong năm 2024. Dù đầu vào kiểm tra kết thúc ngày 28/06, nhãn cuối cùng của mốc 48 giờ vẫn nằm trong dữ liệu đến 30/06/2025. Đây là chia tập theo thời gian, phù hợp với bài toán dự báo.

Mô hình sử dụng `Ridge(alpha=1554.6367)` như một hệ số điều chuẩn cố định cho bài thực hành. Không tối ưu tham số bằng tập kiểm tra. Ridge là hồi quy tuyến tính có điều chuẩn: nó giảm độ lớn các hệ số để mô hình ổn định hơn khi có nhiều đặc trưng liên quan nhau.

### 4.2. Kết quả trên tập kiểm tra

| Dự đoán sau | Số mẫu | RMSE (µg/m³) | MAE (µg/m³) | R² |
|---:|---:|---:|---:|---:|
| 1 giờ | 4.296 | 20,409 | 11,707 | 0,731 |
| 6 giờ | 4.296 | 29,825 | 19,772 | 0,425 |
| 12 giờ | 4.296 | 31,785 | 21,420 | 0,341 |
| 24 giờ | 4.296 | 32,674 | 22,230 | 0,297 |
| 48 giờ | 4.296 | 33,663 | 23,194 | 0,230 |

**RMSE** nhấn mạnh sai số lớn; **MAE** là độ lệch tuyệt đối trung bình; **R²** đo mức độ giải thích biến thiên của nhãn trên tập kiểm tra. Cả RMSE và MAE tăng khi mốc dự đoán xa hơn, còn R² giảm. Điều này cho thấy dự đoán dài hạn khó hơn trong thí nghiệm này.

### 4.3. Giới hạn và hướng phát triển

- Mô hình dùng **thời tiết đã quan trắc tại thời điểm `t`**. Khi sử dụng thực tế, cần có các quan trắc này tại thời điểm đưa ra dự đoán.
- Dữ liệu chỉ thuộc một thành phố và kết thúc vào tháng 6/2025; chưa thể kết luận hiệu quả ở địa điểm hoặc giai đoạn khác.
- 2025 có mức PM2.5 cao hơn các nửa đầu năm trước trong bộ dữ liệu, nên kết quả kiểm tra phản ánh cả sự thay đổi giữa các giai đoạn.
- Có thể phát triển bài sau bằng cách kiểm tra sai số theo mùa hoặc mức ô nhiễm, rồi so sánh thêm với phương pháp dự đoán đơn giản như dùng PM2.5 hiện tại. Phạm vi AIL hiện tại chỉ báo cáo Ridge F4.

## 5. Tái hiện kết quả

Trong thư mục `AIL`, chạy:

```bash
python -m pip install -r requirements.txt
python collect.py
python preprocess.py
python eda.py
python model.py
```

`preprocess.py` tạo lại CSV dùng cho mô hình từ bốn CSV nguồn. `eda.py` ghi bảng thống kê và biểu đồ vào `output/eda/`. `model.py` ghi bảng đánh giá vào `output/metrics.csv` và giá trị thực/dự đoán theo giờ vào `output/predictions.csv`. Các tệp trong `output/` được tạo lại mỗi lần chạy.
