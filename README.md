# Todo List (PyQt5)

Ứng dụng **Todo List** viết bằng **Python 3 + PyQt5**.  
Lưu trữ công việc trong file JSON và hỗ trợ xem theo danh sách, theo ngày, hoặc theo tuần.

---

## 🧩 Tính năng

- Thêm, sửa, xóa, hoàn thành công việc  
- Sắp xếp theo:
  - Ngày hết hạn (`due_dt`)
  - Mức ưu tiên (`priority`)
  - Ngày tạo (`created_at`)
- Lọc công việc theo:
  - Tất cả / Chưa xong / Đã xong  
  - Trong ngày / Trong tuần  
- Hoàn tác thao tác xóa (`Ctrl+Z`)
- Di chuyển thứ tự công việc (khi không lọc/sắp xếp)
- Giao diện trực quan, đa tab:
  1. **Danh sách:** Toàn bộ công việc
  2. **Trong ngày:** Hiển thị công việc theo ngày cụ thể
  3. **Trong tuần:** Hiển thị công việc theo tuần

---

## 📦 Cấu trúc

```
todo.py         # Mã nguồn chính (PyQt5 GUI)
todos.json      # Dữ liệu lưu công việc (tự tạo khi chạy)
```

---

## ⚙️ Cài đặt và chạy

### 1. Cài đặt môi trường
Yêu cầu:
- Python >= 3.8  
- PyQt5

Cài đặt:
```bash
pkgman install python310
pkgman install pyqt5_python310
```

### 2. Chạy chương trình
```bash
python3 todo.py
```

---

## 💾 Dữ liệu

- Lưu tại file `todos.json`
- Cấu trúc mỗi mục:
```json
{
  "text": "Học bài",
  "done": false,
  "priority": 1,
  "due_dt": "2025-11-07 23:59",
  "created_at": "2025-11-07T10:25:33",
  "done_at": null
}
```

---

## ⌨️ Phím tắt

| Tổ hợp | Chức năng |
|--------|------------|
| **Enter** | Thêm công việc |
| **Space** | Đánh dấu hoàn thành |
| **Delete** | Xóa công việc |
| **Ctrl + Z** | Hoàn tác (Undo) |

---

## 🧠 Ghi chú kỹ thuật

- Dữ liệu được tự động sao lưu (`todos.json.bak`) trước khi ghi.  
- Hỗ trợ định dạng ngày: `YYYY-MM-DD HH:MM`  
- Bảng trong tab “Ngày” và “Tuần” chỉ đọc, không chỉnh sửa trực tiếp.
