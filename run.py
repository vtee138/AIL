"""Lệnh chạy tương thích: `python run.py` gọi cùng hàm với `python model.py`.

Toàn bộ phần tạo đặc trưng, huấn luyện và đánh giá nằm trong model.py.
File này chỉ giữ lệnh cũ hoạt động, không chứa thêm một mô hình khác.
"""

from model import main


if __name__ == "__main__":
    main()
