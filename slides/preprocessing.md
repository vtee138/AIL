# Nội dung thay thế cho 4 slide Tiền xử lý

Các slide dưới đây bắt đầu từ `data/collected_pm25_weather.csv` của phần Data Collection và kết thúc ở `data/hanoi_pm25_weather.csv` của phần Preprocessing. Giữ tông xanh đang dùng, nhưng bỏ ảnh chụp bảng/code quá nhỏ và các hình trang trí che nội dung. Mỗi slide chỉ cần một ý chính.

## Slide 1 — Chuẩn hóa CSV đã thu thập

**Tiêu đề trên slide:** CHUẨN HÓA TÊN CỘT VÀ THỜI GIAN

**Nội dung trên slide**

- Đầu vào: `collected_pm25_weather.csv` với **30.341 hàng, 9 cột tên gốc**.
- Đổi tên cột: `Local Time → time`, `PM25 → pm25`, `Temperature → temp`, `Relative Humidity → rh`.
- Chuyển `time` từ chuỗi sang kiểu ngày giờ; các cột khí tượng còn lại cũng dùng tên ngắn.
- Bước chọn cột và gộp bốn năm đã hoàn thành ở *Data Collection*.

**Đoạn mã nếu muốn minh họa (dùng chữ có thể chỉnh sửa, không chụp màn hình):**

```python
data = pd.read_csv(INPUT).rename(columns=COLUMNS)
data["time"] = pd.to_datetime(data["time"])
```

**Lời nói:** CSV từ phần thu thập đã chọn đúng chín cột nhưng vẫn giữ tên và giá trị gốc. Ở bước tiền xử lý, nhóm đổi tên cột và chuyển thời gian sang kiểu ngày giờ để có thể sắp xếp và tạo trục giờ.

## Slide 2 — Trục thời gian liên tục

**Tiêu đề trên slide:** MỖI HÀNG TƯƠNG ỨNG MỘT GIỜ

**Nội dung trên slide**

```text
30.341 hàng đã thu thập → bỏ 5 bản ghi trùng  →  30.336 giờ có dữ liệu
30.336 giờ          →  thêm 24 giờ còn thiếu →  30.360 mốc giờ liên tục
```

- Chuyển `time` sang kiểu ngày giờ, sắp xếp tăng dần và giữ bản ghi cuối nếu trùng giờ.
- Tạo lưới thời gian với tần suất **1 giờ** từ 13/01/2022 đến 30/06/2025.
- Ngày **31/12/2023** thiếu 24 giờ trong dữ liệu gốc; các giờ này được tạo với giá trị `NaN`.

**Lời nói:** Trục giờ liên tục bảo đảm khi lấy PM2.5 cách 24 hàng, đó thật sự là giá trị cách 24 giờ. Bước này tạo vị trí cho giờ thiếu, chưa tự tạo ra quan trắc mới.

**Bỏ khỏi slide cũ:** `is_imputed`. CSV và mã AIL không tạo cột này.

## Slide 3 — Xử lý giá trị thiếu

**Tiêu đề trên slide:** NỘI SUY TỐI ĐA 3 GIỜ

**Nội dung trên slide**

- Dùng nội suy tuyến tính cho **tối đa 3 giờ đầu** trong một khoảng trống có dữ liệu ở hai phía.
- Với khoảng thiếu 24 giờ ngày 31/12/2023: **3 giờ được nội suy, 21 giờ vẫn là `NaN`**.
- Những mẫu có đặc trưng hoặc giá trị cần dự đoán chạm `NaN` sẽ được loại khi tạo dữ liệu học.

**Minh họa nên dùng:**

```text
30/12 23:00       31/12 00:00–02:00       31/12 03:00–23:00       01/01 00:00
 Có dữ liệu   →      Nội suy 3 giờ     →        21 giờ NaN      →    Có dữ liệu
```

**Đoạn mã trên slide:**

```python
data = data.interpolate(limit=3, limit_area="inside")
```

**Lời nói:** `limit=3` không có nghĩa là chỉ xử lý những khoảng trống dài tối đa 3 giờ. Với khoảng trống dài 24 giờ trong bộ dữ liệu này, pandas điền ba giờ đầu và giữ 21 giờ còn lại là thiếu. Vì vậy hình minh họa nên dùng đúng tình huống thực tế này.

## Slide 4 — Dataset sau tiền xử lý

**Tiêu đề trên slide:** DATASET DÙNG CHO MÔ HÌNH

**Nội dung trên slide**

| Quy mô | Giá trị |
|---|---:|
| Mốc giờ liên tục | **30.360** |
| Cột | **9** = `time` + `pm25` + 7 biến thời tiết |
| Hàng đầy đủ giá trị | **30.339** |
| Giờ còn thiếu | **21** |

**Dòng dưới bảng:** `data/hanoi_pm25_weather.csv` · 13/01/2022 00:00 – 30/06/2025 23:00

**Lời nói:** Đây là CSV đầu vào của bước EDA và mô hình. 21 giờ thiếu được giữ đúng vị trí trên trục thời gian. Khi mô hình tạo các độ trễ và nhãn tương lai, số mẫu hợp lệ sẽ ít hơn 30.339; đó là bước xử lý riêng ở phần Model.

**Bỏ khỏi slide cũ:** ảnh bảng 15 cột, `aqi`, `co`, các chất ô nhiễm khác và `is_imputed`. Chúng không có trong CSV AIL.

## Lưu ý dàn trang chung

- Dùng một kiểu tiêu đề và một cỡ chữ nội dung cho cả bốn slide; mỗi slide giữ tối đa 3–4 ý ngắn.
- Thay ảnh chụp code bằng đoạn code có thể sửa, phóng đủ lớn để đọc từ cuối lớp.
- Giảm họa tiết nền, sticker và mũi tên trang trí. Ưu tiên sơ đồ số liệu ở slide 2 và dòng thời gian ở slide 3.
- Đặt dòng nguồn nhỏ ở chân phần: `Nguồn: Kaggle, AQI in Hanoi 2022–2025 (v1); xử lý bằng AIL/preprocess.py`.
