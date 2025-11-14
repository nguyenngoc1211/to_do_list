# HƯỚNG DẪN ĐỌC CODE TODO.PY

## 📋 TỔNG QUAN

File `todo.py` là ứng dụng quản lý công việc (Todo List) sử dụng PyQt5. Ứng dụng cho phép:
- Thêm, sửa, xóa công việc
- Đặt ưu tiên và hạn chót cho công việc
- Xem công việc theo ngày, tuần, và công việc quá hạn
- Nhận thông báo khi công việc đến hạn

---

## 🗂️ CẤU TRÚC FILE

### 1. PHẦN IMPORT VÀ CẤU HÌNH (Dòng 1-250)
```python
# Import các thư viện cần thiết
import json, os, shutil, sys
from datetime import datetime, date, timedelta
from PyQt5 import QtWidgets, QtCore, QtGui

# Các hằng số cấu hình
BASE_DIR = ...        # Thư mục chứa file chương trình
DATA_FILE = ...       # File JSON lưu dữ liệu
DT_FMT = ...         # Định dạng ngày giờ
APP_STYLESHEET = ... # CSS cho giao diện
```

**Giải thích:**
- `BASE_DIR`: Đường dẫn thư mục chứa file todo.py
- `DATA_FILE`: File todos.json lưu tất cả công việc
- `DT_FMT`: Định dạng "2025-11-15 14:30"
- `APP_STYLESHEET`: Chuỗi CSS định nghĩa màu sắc, font chữ, bo góc...

---

### 2. CÁC HÀM TIỆN ÍCH (Dòng 252-362)

#### `now_iso()` - Lấy thời gian hiện tại
```python
def now_iso():
    return datetime.now().isoformat(timespec="seconds")
# Ví dụ: "2025-11-15T14:30:00"
```

#### `start_of_week(d)` - Tìm ngày đầu tuần (Thứ Hai)
```python
start_of_week(date(2025, 11, 15))  # Trả về 2025-11-11 (Thứ Hai)
```

#### `end_of_week(d)` - Tìm ngày cuối tuần (Chủ Nhật)
```python
end_of_week(date(2025, 11, 15))  # Trả về 2025-11-17 (Chủ Nhật)
```

#### `parse_dt(s)` - Chuyển chuỗi thành datetime
```python
parse_dt("2025-11-15 14:30")  # Trả về datetime(2025, 11, 15, 14, 30)
```

---

### 3. LỚP STORE - QUẢN LÝ DỮ LIỆU (Dòng 365-466)

**Mục đích:** Đọc/ghi dữ liệu công việc vào file JSON

#### Cấu trúc dữ liệu công việc:
```python
{
    "text": "Làm bài tập",           # Nội dung công việc
    "done": False,                    # Đã hoàn thành chưa
    "priority": 1,                    # Mức ưu tiên (0=thấp, 1=thường, 2=cao)
    "due_dt": "2025-11-15 23:59",    # Hạn chót
    "created_at": "2025-11-15T10:00:00", # Thời gian tạo
    "done_at": None,                  # Thời gian hoàn thành
    "note": "Ghi chú thêm",          # Ghi chú
    "notified": False                 # Đã thông báo chưa
}
```

#### Các phương thức quan trọng:

**`load()`** - Đọc dữ liệu từ file
```python
store = Store("todos.json")
store.load()  # Đọc file vào store.items
```

**`save()`** - Lưu dữ liệu vào file
```python
store.save()  # Lưu store.items vào file (tạo backup trước)
```

**`migrate(it)`** - Chuẩn hóa dữ liệu
- Đảm bảo mọi công việc có đầy đủ các trường cần thiết
- Chuyển đổi dữ liệu cũ sang định dạng mới

---

### 4. LỚP TASKDIALOG - HỘP THOẠI THÊM/SỬA (Dòng 469-627)

**Mục đích:** Hiển thị form để người dùng nhập thông tin công việc

#### Các thành phần giao diện:
- `text_edit` (QLineEdit): Ô nhập tiêu đề công việc
- `priority_combo` (QComboBox): Chọn mức ưu tiên
- `due_checkbox` (QCheckBox): Bật/tắt chọn hạn chót
- `due_edit` (QDateTimeEdit): Chọn ngày giờ hạn chót
- `note_edit` (QPlainTextEdit): Nhập ghi chú

#### Các phương thức:

**`get_data()`** - Lấy dữ liệu từ form
```python
dialog = TaskDialog(title="Thêm công việc")
if dialog.exec_() == Accepted:
    data = dialog.get_data()
    # data = {"text": "...", "priority": 1, "due_dt": "...", "note": "..."}
```

---

### 5. LỚP MAIN - CỬA SỔ CHÍNH (Dòng 630-1968)

**Mục đích:** Quản lý giao diện chính và logic ứng dụng

#### 5.1. Khởi tạo `__init__()` (Dòng 645-710)
```python
# Tạo Store để quản lý dữ liệu
self.store = Store(DATA_FILE)
self.store.load()

# Tạo 4 tab
tabs.addTab(self.tab_list, "Danh sách")      # Tab 1
tabs.addTab(self.tab_day, "Trong ngày")      # Tab 2
tabs.addTab(self.tab_week, "Trong tuần")     # Tab 3
tabs.addTab(self.tab_overdue, "Quá hạn")     # Tab 4

# Thiết lập Timer kiểm tra công việc đến hạn mỗi phút
self.check_timer.start(60000)  # 60,000 ms = 1 phút
```

#### 5.2. CÁC HÀM CRUD (Dòng 1331-1509)

**`add_item()`** - Thêm công việc mới
```python
def add_item(self):
    # 1. Hiển thị dialog
    dialog = TaskDialog(...)

    # 2. Thêm vào store
    self.store.items.append({...})

    # 3. Làm mới giao diện và lưu file
    self.refresh_all()
    self.store.save()
```

**`edit_item()`** - Sửa công việc
```python
def edit_item(self):
    # 1. Lấy công việc đang chọn
    idx = self._current_index()
    it = self.store.items[idx]

    # 2. Hiển thị dialog với dữ liệu hiện tại
    dialog = TaskDialog(..., task=it)

    # 3. Cập nhật dữ liệu
    it["text"] = data["text"]
    it["notified"] = False  # Reset để thông báo lại
```

**`delete_item()`** - Xóa công việc
```python
def delete_item(self):
    # 1. Xác nhận với người dùng
    if MessageBox.question(...) == Yes:
        # 2. Lưu để có thể hoàn tác
        self._undo = ("del", idx, dict(item))

        # 3. Xóa
        del self.store.items[idx]
```

**`toggle_done()`** - Đánh dấu hoàn thành
```python
def toggle_done(self):
    it["done"] = not it["done"]
    it["done_at"] = now_iso() if it["done"] else None

    # Reset notified để có thể nhận thông báo lại
    if not it["done"]:
        it["notified"] = False
```

#### 5.3. LỌC VÀ SẮP XẾP (Dòng 1511-1604)

**`_filtered_indices()`** - Lọc công việc theo điều kiện
```python
def _filtered_indices(self):
    # Lọc theo:
    # - Từ khóa tìm kiếm (q)
    # - Trạng thái (all/todo/done)
    # - Phạm vi (all/today/week)

    # Sắp xếp theo:
    # - default: Thứ tự thêm vào
    # - due_dt: Hạn chót sớm nhất lên đầu
    # - priority: Ưu tiên cao lên đầu
    # - created_at: Tạo mới nhất lên đầu
```

#### 5.4. LÀM MỚI GIAO DIỆN (Dòng 1606-1817)

**`refresh_list()`** - Làm mới tab Danh sách
```python
def refresh_list(self):
    # 1. Xóa danh sách cũ
    self.list.clear()

    # 2. Lọc công việc
    filtered = self._filtered_indices()

    # 3. Tạo widget cho mỗi công việc
    for idx in filtered:
        widget = self._make_task_widget(it)
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)

    # 4. Cập nhật thống kê
    self._update_statistics()
```

**`refresh_day()`** - Làm mới tab Trong ngày
```python
def refresh_day(self):
    # Lọc công việc có hạn chót = ngày được chọn
    # Hiển thị trong QTableWidget
```

**`refresh_week()`** - Làm mới tab Trong tuần
```python
def refresh_week(self):
    # Lọc công việc có hạn chót trong tuần được chọn
    # Hiển thị trong QTableWidget
```

**`refresh_overdue()`** - Làm mới tab Quá hạn
```python
def refresh_overdue(self):
    # Lọc công việc: chưa xong VÀ hạn chót < bây giờ
    # Hiển thị trong QTableWidget
```

**`refresh_all()`** - Làm mới tất cả tab
```python
def refresh_all(self):
    self.refresh_list()
    self.refresh_day()
    self.refresh_week()
    self.refresh_overdue()
```

#### 5.5. HỆ THỐNG THÔNG BÁO (Dòng 1819-1968)

**`check_due_tasks()`** - Kiểm tra công việc đến hạn (gọi mỗi phút)
```python
def check_due_tasks(self):
    now = datetime.now()
    tasks_to_notify = []

    # Tìm công việc: chưa xong, chưa thông báo, đã đến hạn
    for task in self.store.items:
        if task["done"] or task["notified"]:
            continue

        due_dt = parse_dt(task["due_dt"])
        if due_dt and due_dt <= now:
            tasks_to_notify.append(task)

    if tasks_to_notify:
        # Gửi thông báo system tray
        self.show_notification(title, message)

        # Thêm vào danh sách thông báo trong app
        for task in tasks_to_notify:
            self.app_notifications.append(...)

        # Đánh dấu đã thông báo
        task["notified"] = True
        self.store.save()
```

**`show_notification()`** - Hiển thị thông báo Windows
```python
def show_notification(self, title, message):
    self.tray_icon.showMessage(title, message, 3000)
    # Hiển thị thông báo ở góc màn hình trong 3 giây
```

**`show_app_notifications()`** - Hiển thị menu thông báo
```python
def show_app_notifications(self):
    # Hiển thị menu pop-up với:
    # - Danh sách thông báo
    # - Nút "Đánh dấu đã đọc"
```

---

### 6. HÀM MAIN (Dòng 1972-2003)

```python
def main():
    # 1. Tạo QApplication
    app = QtWidgets.QApplication(sys.argv)

    # 2. Thiết lập font
    app.setFont(QtGui.QFont("Segoe UI", 9))

    # 3. Tạo và hiển thị cửa sổ chính
    w = Main()
    w.show()

    # 4. Chạy vòng lặp sự kiện
    sys.exit(app.exec_())
```

---

## 🔄 LUỒNG HOẠT ĐỘNG CHÍNH

### Khi khởi động ứng dụng:
```
1. main() được gọi
2. Tạo QApplication
3. Tạo Main window
   ├─ Tải dữ liệu từ todos.json (store.load())
   ├─ Tạo 4 tab
   ├─ Thiết lập Timer (kiểm tra mỗi phút)
   └─ Hiển thị giao diện
4. Chạy vòng lặp sự kiện (app.exec_())
```

### Khi thêm công việc:
```
1. Người dùng nhập thông tin và nhấn "Thêm"
2. add_item() được gọi
   ├─ Hiển thị TaskDialog
   ├─ Lấy dữ liệu từ dialog
   ├─ Thêm vào store.items
   ├─ refresh_all() (làm mới giao diện)
   └─ store.save() (lưu file)
```

### Khi kiểm tra công việc đến hạn:
```
1. Timer hết giờ (mỗi 60 giây)
2. check_due_tasks() được gọi
   ├─ Duyệt tất cả công việc
   ├─ Tìm công việc: chưa xong + chưa thông báo + đã đến hạn
   ├─ Gửi thông báo system tray
   ├─ Thêm vào app_notifications
   ├─ Đánh dấu notified = True
   └─ Lưu file
```

---

## 🎨 CẤU TRÚC GIAO DIỆN

```
Main Window
├─ Tab 1: Danh sách
│  ├─ Card Header (tiêu đề + thanh progress + nút thông báo)
│  ├─ Card Input (thêm công việc nhanh)
│  ├─ Card Filter (tìm kiếm, sắp xếp, lọc)
│  └─ Card List (danh sách công việc)
│     └─ Các nút: Hoàn thành, Sửa, Xóa, Hoàn tác, Lên, Xuống
│
├─ Tab 2: Trong ngày
│  └─ Bảng hiển thị công việc có hạn chót trong ngày được chọn
│
├─ Tab 3: Trong tuần
│  └─ Bảng hiển thị công việc có hạn chót trong tuần được chọn
│
└─ Tab 4: Quá hạn
   └─ Bảng hiển thị công việc chưa xong và đã quá hạn
```

---

## 📊 DỮ LIỆU ĐƯỢC LƯU NHƯ THẾ NÀO?

File `todos.json` lưu mảng các công việc:
```json
[
  {
    "text": "Làm bài tập Hệ điều hành",
    "done": false,
    "priority": 2,
    "due_dt": "2025-11-20 23:59",
    "created_at": "2025-11-15T10:00:00",
    "done_at": null,
    "note": "Bài 3, 4, 5",
    "notified": false
  },
  {
    "text": "Đi mua sữa",
    "done": true,
    "priority": 0,
    "due_dt": null,
    "created_at": "2025-11-14T08:00:00",
    "done_at": "2025-11-14T09:30:00",
    "note": null,
    "notified": false
  }
]
```

Mỗi lần `store.save()` được gọi:
1. Tạo backup: `todos.json.bak`
2. Ghi đè file `todos.json` mới

---

## ⚠️ CÁC LƯU Ý QUAN TRỌNG

### 1. Index thực vs Index hiển thị
- Danh sách có thể bị lọc → Index hiển thị ≠ Index thực trong store.items
- Luôn dùng `_current_index()` để lấy index thực
- `_filtered_indices()` trả về mapping giữa 2 loại index

### 2. Reset trạng thái thông báo
- Khi sửa công việc: `notified = False`
- Khi bỏ đánh dấu hoàn thành: `notified = False`
- Để có thể nhận thông báo lại nếu vẫn quá hạn

### 3. Kiểm tra quá hạn
```python
now = datetime.now()
overdue = (due_dt < now) and not task["done"]
```
- Chỉ công việc chưa xong mới tính là quá hạn

### 4. Làm mới style động
- Khi thay đổi property (ví dụ: done=True/False)
- Phải gọi `_refresh_widget_style()` để Qt áp dụng lại CSS

---

## 🐛 KIỂM TRA LỖI

### Kiểm tra syntax:
```bash
python -m py_compile todo.py
```

### Chạy thử:
```bash
python todo.py
```

### Các lỗi thường gặp:
1. **FileNotFoundError**: Tạo file `todos.json` rỗng
2. **JSONDecodeError**: Xóa file `todos.json` và khởi động lại
3. **Không thông báo**: Kiểm tra system tray có khả dụng không

---

## 📚 TÀI LIỆU THAM KHẢO

- **PyQt5 Documentation**: https://doc.qt.io/qtforpython/
- **Python datetime**: https://docs.python.org/3/library/datetime.html
- **JSON trong Python**: https://docs.python.org/3/library/json.html

---

**Tác giả:** [Tên của bạn]
**Ngày cập nhật:** 2025-11-15
**Phiên bản:** 1.0
