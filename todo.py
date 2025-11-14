#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ỨNG DỤNG QUẢN LÝ CÔNG VIỆC (TODO LIST)
Ứng dụng desktop sử dụng PyQt5 để quản lý danh sách công việc với các tính năng:
- Thêm, sửa, xóa công việc
- Đặt ưu tiên và hạn chót
- Xem công việc theo ngày, tuần, công việc quá hạn
- Thông báo công việc đến hạn
"""

# Import các thư viện cần thiết
import json, os, shutil, sys
from datetime import datetime, date, timedelta

from PyQt5 import QtWidgets, QtCore, QtGui

# ============================================================================
# CÁC HẰNG SỐ CẤU HÌNH
# ============================================================================

# Đường dẫn thư mục chứa file chương trình
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn file JSON lưu trữ dữ liệu công việc
DATA_FILE = os.path.join(BASE_DIR, "todos.json")

# Định dạng ngày giờ: 2025-11-15 14:30
DT_FMT = "%Y-%m-%d %H:%M"

# Định dạng ngày: 2025-11-15
D_FMT  = "%Y-%m-%d"

# Mảng tên thứ trong tuần (tiếng Việt)
WEEKDAY_VN = ["Th 2","Th 3","Th 4","Th 5","Th 6","Th 7","CN"]

# Định dạng ngày cho QDateEdit của PyQt5
QT_D_FMT = "yyyy-MM-dd"

# Định dạng ngày giờ cho QDateTimeEdit của PyQt5
QT_DT_FMT = "yyyy-MM-dd HH:mm"

# ============================================================================
# CSS STYLESHEET - ĐỊNH DẠNG GIAO DIỆN
# ============================================================================
# Chuỗi CSS này định nghĩa toàn bộ giao diện của ứng dụng
# Sử dụng QSS (Qt Style Sheets) - tương tự CSS cho web
APP_STYLESHEET = """
/* todo-theme */
QMainWindow { background-color: #f4f6fb; }
QTabWidget::pane { border: 0px; }
QTabBar::tab {
    padding: 10px 20px;
    border-radius: 10px;
    margin: 6px 4px;
    color: #4d5a73;
    background: #e6ebfa;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #4c6ef5;
    color: white;
}
QFrame#card {
    background: #ffffff;
    border: 1px solid #dfe4f5;
    border-radius: 16px;
}
QLabel#cardTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1f2d3d;
}
QLabel#cardSubtitle {
    color: #647094;
    font-size: 13px;
}
QLabel#cardSubtitle[done="true"] {
    color: #9aa3b9;
}
QLabel#statsLabel {
    font-size: 16px;
    font-weight: 600;
    color: #4c6ef5;
}
QLabel#placeholder {
    color: #8f96a6;
    font-size: 15px;
}
QPushButton, QToolButton {
    background-color: #4c6ef5;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover, QToolButton:hover {
    background-color: #3b5bdb;
}
QPushButton:disabled, QToolButton:disabled {
    background-color: #ccd4ff;
    color: #f8f9ff;
}
QPushButton[secondary="true"], QToolButton[secondary="true"] {
    background-color: #ecf0ff;
    color: #4c6ef5;
}
QPushButton[secondary="true"]:hover, QToolButton[secondary="true"]:hover {
    background-color: #dee4ff;
}
QPushButton[danger="true"] {
    background-color: #fa5252;
    color: #ffffff;
}
QPushButton[danger="true"]:hover {
    background-color: #f03e3e;
}
QComboBox, QDateEdit, QLineEdit {
    border: 1px solid #d2d8ea;
    border-radius: 10px;
    padding: 6px 10px;
    background-color: #ffffff;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #4c6ef5;
}
QListWidget#taskList {
    border: none;
    background-color: transparent;
}
QListWidget#taskList::item {
    margin: 6px 10px;
    border-radius: 12px;
    padding: 12px 14px;
}
QListWidget#taskList::item:selected {
    background-color: rgba(76, 110, 245, 0.16);
    color: #1f2d3d;
}
QTableWidget {
    border: none;
    background-color: transparent;
    gridline-color: #e1e7fb;
}
QHeaderView::section {
    background-color: #f0f3ff;
    border: none;
    padding: 9px;
    font-weight: 600;
    color: #4d5a73;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle {
    background: rgba(76, 110, 245, 0.35);
    border-radius: 6px;
}
QScrollBar::handle:hover {
    background: rgba(76, 110, 245, 0.5);
}
QFrame#taskCard {
    background: #f9faff;
    border: 2px solid transparent;
    border-radius: 16px;
    padding: 14px 16px;
}
QFrame#taskCard[selected="true"] {
    border-color: #4c6ef5;
    box-shadow: 0 6px 18px rgba(76, 110, 245, 0.18);
}
QFrame#taskCard[done="true"] {
    background: #eef2ff;
}
QLabel#taskTitle {
    font-size: 15px;
    font-weight: 600;
    color: #1f2d3d;
}
QLabel#taskTitle[done="true"] {
    color: #7a839b;
    text-decoration: line-through;
}
QLabel#badge {
    font-size: 24px;
    min-width: 36px;
    color: #4c6ef5;
}
QLabel#badge[done="true"] {
    color: #2b8a3e;
}
QLabel#badge[overdue="true"] {
    color: #e03131;
}
QLabel#chip {
    border-radius: 999px;
    padding: 4px 14px;
    font-weight: 600;
    font-size: 12px;
    background: #e7ecff;
    color: #42527a;
}
QLabel#chip[compact="true"] {
    padding: 3px 10px;
    font-weight: 500;
}
QLabel#chip[variant="status-done"] {
    background: #d3f9d8;
    color: #2b8a3e;
}
QLabel#chip[variant="status-todo"] {
    background: #fff3bf;
    color: #d9480f;
}
QLabel#chip[variant="priority-high"] {
    background: #ffe3e3;
    color: #e03131;
}
QLabel#chip[variant="priority-normal"] {
    background: #dee2ff;
    color: #3b5bdb;
}
QLabel#chip[variant="priority-low"] {
    background: #e6fcf5;
    color: #0ca678;
}
QLabel#chip[variant="due"] {
    background: #dbe4ff;
    color: #3b5bdb;
}
QLabel#chip[variant="overdue"] {
    background: #ffe3e3;
    color: #c92a2a;
}
QProgressBar {
    background: #e7ecff;
    border-radius: 999px;
    border: 1px solid transparent;
    color: #1f2d3d;
    text-align: center;
    padding: 2px;
}
QProgressBar::chunk {
    border-radius: 999px;
    background: #4c6ef5;
}
"""

# ============================================================================
# CÁC HÀM TIỆN ÍCH (UTILITY FUNCTIONS)
# ============================================================================

def now_iso():
    """
    Lấy thời gian hiện tại và trả về dạng chuỗi ISO 8601.

    Returns:
        str: Chuỗi thời gian dạng "2025-11-15T14:30:00"

    Ví dụ: "2025-11-15T14:30:00"
    """
    return datetime.now().isoformat(timespec="seconds")


def start_of_week(d: date) -> date:
    """
    Tìm ngày đầu tuần (Thứ Hai) của một ngày bất kỳ.

    Args:
        d (date): Ngày cần tìm đầu tuần

    Returns:
        date: Ngày thứ Hai của tuần đó

    Ví dụ: Nếu d = 15/11/2025 (Thứ Sáu) → trả về 11/11/2025 (Thứ Hai)
    """
    return d - timedelta(days=d.weekday())


def end_of_week(d: date) -> date:
    """
    Tìm ngày cuối tuần (Chủ Nhật) của một ngày bất kỳ.

    Args:
        d (date): Ngày cần tìm cuối tuần

    Returns:
        date: Ngày Chủ Nhật của tuần đó

    Ví dụ: Nếu d = 15/11/2025 (Thứ Sáu) → trả về 17/11/2025 (Chủ Nhật)
    """
    return start_of_week(d) + timedelta(days=6)


def parse_dt(s):
    """
    Chuyển đổi chuỗi thành đối tượng datetime.

    Args:
        s (str): Chuỗi ngày giờ dạng "2025-11-15 14:30"

    Returns:
        datetime hoặc None: Đối tượng datetime nếu hợp lệ, None nếu lỗi

    Ví dụ: "2025-11-15 14:30" → datetime(2025, 11, 15, 14, 30)
    """
    try:
        return datetime.strptime(s, DT_FMT) if s else None
    except Exception:
        return None


def qdatetime_from_str(s):
    """
    Chuyển đổi chuỗi thành đối tượng QDateTime của PyQt5.

    Args:
        s (str): Chuỗi ngày giờ

    Returns:
        QDateTime: Đối tượng QDateTime (nếu lỗi thì trả về thời gian hiện tại)

    Hàm này thử nhiều cách parse:
    1. Parse trực tiếp theo định dạng QT_DT_FMT
    2. Nếu thất bại, dùng hàm parse_dt() rồi chuyển sang QDateTime
    3. Nếu tất cả thất bại, trả về thời gian hiện tại
    """
    if not s:
        return QtCore.QDateTime.currentDateTime()

    # Thử parse theo định dạng Qt
    qdt = QtCore.QDateTime.fromString(s, QT_DT_FMT)
    if qdt.isValid():
        return qdt

    # Thử parse theo định dạng Python rồi chuyển sang Qt
    dt = parse_dt(s)
    if not dt:
        return QtCore.QDateTime.currentDateTime()

    return QtCore.QDateTime(
        QtCore.QDate(dt.year, dt.month, dt.day),
        QtCore.QTime(dt.hour, dt.minute, dt.second)
    )


def format_qdatetime(dt: QtCore.QDateTime) -> str:
    """
    Định dạng đối tượng QDateTime thành chuỗi.

    Args:
        dt (QDateTime): Đối tượng QDateTime cần format

    Returns:
        str: Chuỗi ngày giờ dạng "2025-11-15 14:30" hoặc "" nếu không hợp lệ
    """
    if not dt or not dt.isValid():
        return ""
    return dt.toString(QT_DT_FMT)


# ============================================================================
# LỚP STORE - QUẢN LÝ DỮ LIỆU (DATA STORAGE)
# ============================================================================

class Store:
    """
    Lớp quản lý việc đọc/ghi dữ liệu công việc vào file JSON.

    Attributes:
        path (str): Đường dẫn đến file JSON lưu trữ
        items (list): Danh sách các công việc (mỗi công việc là một dict)
    """

    def __init__(self, path):
        """
        Khởi tạo Store với đường dẫn file.

        Args:
            path (str): Đường dẫn đến file JSON
        """
        self.path = path
        self.items = []

    def migrate(self, it):
        """
        Chuyển đổi và chuẩn hóa dữ liệu công việc.

        Hàm này đảm bảo mọi công việc có đầy đủ các trường cần thiết,
        và chuyển đổi dữ liệu cũ sang định dạng mới (nếu cần).

        Args:
            it: Dữ liệu công việc (có thể là dict hoặc string)

        Returns:
            dict: Công việc đã được chuẩn hóa với đầy đủ các trường:
                - text (str): Nội dung công việc
                - done (bool): Trạng thái hoàn thành
                - priority (int): Mức ưu tiên (0=thấp, 1=thường, 2=cao)
                - due_dt (str): Hạn chót dạng "2025-11-15 14:30"
                - created_at (str): Thời gian tạo dạng ISO
                - done_at (str): Thời gian hoàn thành
                - note (str): Ghi chú
                - notified (bool): Đã thông báo chưa
        """
        # Chuyển thành dict nếu chưa phải
        it = dict(it) if isinstance(it, dict) else {"text": str(it)}

        # Đảm bảo có đầy đủ các trường
        it.setdefault("text", "")
        it.setdefault("done", False)
        it.setdefault("priority", 1)  # 0=thấp, 1=thường, 2=cao

        # Nâng cấp từ định dạng cũ (due) sang định dạng mới (due_dt)
        if "due_dt" not in it:
            due = it.get("due")  # Định dạng cũ chỉ có ngày
            it["due_dt"] = f"{due} 23:59" if due else None
        it.pop("due", None)  # Xóa trường cũ

        it.setdefault("created_at", now_iso())
        it.setdefault("done_at", None)
        it.setdefault("note", None)
        it.setdefault("notified", False)  # Đã gửi thông báo chưa
        return it

    def load(self):
        """
        Tải dữ liệu từ file JSON vào bộ nhớ.

        Nếu file không tồn tại hoặc bị lỗi, sẽ khởi tạo danh sách rỗng
        và hiện thông báo lỗi cho người dùng.
        """
        if not os.path.exists(self.path):
            self.items = []
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Chuẩn hóa từng công việc
            self.items = [self.migrate(x) for x in (raw if isinstance(raw, list) else [])]
        except Exception as e:
            self.items = []
            QtWidgets.QMessageBox.warning(None, "Lỗi đọc dữ liệu",
                                          f"Không thể đọc tệp {os.path.basename(self.path)}:\n{e}")

    def save(self):
        """
        Lưu dữ liệu từ bộ nhớ vào file JSON.

        Trước khi lưu, sẽ tạo bản sao lưu (.bak) của file hiện tại.
        Nếu có lỗi, sẽ hiển thị thông báo lỗi.
        """
        try:
            # Tạo bản backup trước khi ghi đè
            if os.path.exists(self.path):
                shutil.copyfile(self.path, self.path + ".bak")

            # Ghi dữ liệu vào file JSON với indent đẹp
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi lưu", str(e))


# ============================================================================
# LỚP TASKDIALOG - HỘP THOẠI THÊM/SỬA CÔNG VIỆC
# ============================================================================

class TaskDialog(QtWidgets.QDialog):
    """
    Hộp thoại (Dialog) để thêm mới hoặc chỉnh sửa công việc.

    Cho phép người dùng nhập:
    - Tiêu đề công việc
    - Mức ưu tiên
    - Hạn chót (tùy chọn)
    - Ghi chú (tùy chọn)
    """

    def __init__(self, parent=None, *, title="Thêm công việc", task=None):
        """
        Khởi tạo hộp thoại.

        Args:
            parent: Widget cha
            title (str): Tiêu đề của hộp thoại
            task (dict): Dữ liệu công việc để chỉnh sửa (None nếu thêm mới)
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)  # Chặn tương tác với cửa sổ khác
        self.setMinimumWidth(420)

        # Layout chính
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Tiêu đề
        title_lbl = QtWidgets.QLabel("Chi tiết công việc")
        title_lbl.setObjectName("cardTitle")
        layout.addWidget(title_lbl)

        # Form nhập liệu
        form = QtWidgets.QFormLayout()
        form.setSpacing(12)
        layout.addLayout(form)

        # Ô nhập tiêu đề công việc
        self.text_edit = QtWidgets.QLineEdit()
        self.text_edit.setPlaceholderText("Nội dung công việc")
        form.addRow("Tiêu đề", self.text_edit)

        # ComboBox chọn mức ưu tiên
        self.priority_combo = QtWidgets.QComboBox()
        self.priority_combo.addItem("Thấp", 0)
        self.priority_combo.addItem("Thường", 1)
        self.priority_combo.addItem("Cao", 2)
        form.addRow("Ưu tiên", self.priority_combo)

        # Checkbox bật/tắt chọn hạn chót
        due_row = QtWidgets.QHBoxLayout()
        due_row.setSpacing(8)
        self.due_checkbox = QtWidgets.QCheckBox("Đặt hạn chót")
        self.due_checkbox.toggled.connect(self._sync_due_state)
        due_row.addWidget(self.due_checkbox)
        due_row.addStretch()
        form.addRow("", due_row)

        # Ô chọn ngày giờ hạn chót
        self.due_edit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.due_edit.setDisplayFormat(QT_DT_FMT)
        self.due_edit.setCalendarPopup(True)  # Hiển thị lịch khi click
        self.due_edit.setEnabled(False)  # Mặc định vô hiệu hóa
        form.addRow("Hạn chót", self.due_edit)

        # Ô nhập ghi chú
        self.note_edit = QtWidgets.QPlainTextEdit()
        self.note_edit.setPlaceholderText("Ghi chú (tuỳ chọn)")
        self.note_edit.setFixedHeight(80)
        form.addRow("Ghi chú", self.note_edit)

        # Nút Lưu và Hủy
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save
        )
        self.button_box.accepted.connect(self._accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Nếu có dữ liệu task (chế độ chỉnh sửa), điền vào form
        if task:
            self.text_edit.setText(task.get("text", ""))

            # Chọn mức ưu tiên
            target_idx = self.priority_combo.findData(int(task.get("priority", 1)))
            if target_idx != -1:
                self.priority_combo.setCurrentIndex(target_idx)

            # Điền hạn chót nếu có
            due = task.get("due_dt")
            if due:
                self.due_checkbox.setChecked(True)
                self.due_edit.setDateTime(qdatetime_from_str(due))

            # Điền ghi chú nếu có
            note = task.get("note")
            if note:
                self.note_edit.setPlainText(note)

        self._sync_due_state()

    def _sync_due_state(self):
        """
        Đồng bộ trạng thái kích hoạt của ô chọn hạn chót.

        Ô chọn hạn chót chỉ được kích hoạt khi checkbox được tích.
        """
        self.due_edit.setEnabled(self.due_checkbox.isChecked())

    def _accept(self):
        """
        Xử lý khi người dùng nhấn nút Lưu.

        Kiểm tra xem tiêu đề có trống không. Nếu trống, hiện cảnh báo.
        Nếu hợp lệ, đóng dialog với trạng thái Accepted.
        """
        text = self.text_edit.text().strip()
        if not text:
            QtWidgets.QMessageBox.warning(
                self, "Thiếu thông tin", "Vui lòng nhập nội dung công việc."
            )
            return
        self.accept()

    def get_data(self):
        """
        Lấy dữ liệu từ form.

        Returns:
            dict: Dictionary chứa các thông tin:
                - text (str): Tiêu đề công việc
                - priority (int): Mức ưu tiên
                - due_dt (str hoặc None): Hạn chót
                - note (str hoặc None): Ghi chú
        """
        text = self.text_edit.text().strip()
        priority = int(self.priority_combo.currentData())

        # Lấy hạn chót nếu checkbox được tích
        due = None
        if self.due_checkbox.isChecked():
            due_str = format_qdatetime(self.due_edit.dateTime())
            due = due_str or None

        note = self.note_edit.toPlainText().strip() or None

        return {
            "text": text,
            "priority": priority,
            "due_dt": due,
            "note": note
        }


# ============================================================================
# LỚP MAIN - CỬA SỔ CHÍNH CỦA ỨNG DỤNG
# ============================================================================

class Main(QtWidgets.QMainWindow):
    """
    Lớp cửa sổ chính của ứng dụng Todo List.

    Quản lý:
    - Giao diện chính với 4 tab (Danh sách, Trong ngày, Trong tuần, Quá hạn)
    - Thêm, sửa, xóa, hoàn thành công việc
    - Lọc, tìm kiếm, sắp xếp công việc
    - Thông báo công việc đến hạn
    """

    def __init__(self):
        """
        Khởi tạo cửa sổ chính và thiết lập giao diện.
        """
        super().__init__()
        self.setWindowTitle("Todo List")
        self.resize(1040, 660)

        # Áp dụng theme CSS
        self._apply_theme()

        # Khởi tạo Store để quản lý dữ liệu
        self.store = Store(DATA_FILE)
        self.store.load()
        self._undo = None  # Lưu trạng thái để hoàn tác

        # Danh sách thông báo trong app (hiển thị ở chuông)
        self.app_notifications = []

        # Tạo TabWidget chứa 4 tab
        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # Tab 1: Danh sách tất cả công việc
        self.tab_list = QtWidgets.QWidget()
        tabs.addTab(self.tab_list, "Danh sách")
        self._build_tab_list()

        # Tab 2: Công việc trong ngày
        self.tab_day = QtWidgets.QWidget()
        tabs.addTab(self.tab_day, "Trong ngày")
        self._build_tab_day()

        # Tab 3: Công việc trong tuần
        self.tab_week = QtWidgets.QWidget()
        tabs.addTab(self.tab_week, "Trong tuần")
        self._build_tab_week()

        # Tab 4: Công việc quá hạn
        self.tab_overdue = QtWidgets.QWidget()
        tabs.addTab(self.tab_overdue, "Quá hạn")
        self._build_tab_overdue()

        # Làm mới tất cả các tab
        self.refresh_all()

        # ===== THIẾT LẬP HỆ THỐNG THÔNG BÁO =====

        # Tạo biểu tượng system tray (vùng thông báo Windows)
        self.tray_icon = None
        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QtWidgets.QSystemTrayIcon(self)
            # Sử dụng icon mặc định của Qt
            icon = self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("Todo List")
            self.tray_icon.show()

        # Thiết lập Timer để kiểm tra công việc đến hạn mỗi phút
        self.check_timer = QtCore.QTimer(self)
        self.check_timer.timeout.connect(self.check_due_tasks)
        self.check_timer.start(60000)  # 60,000 ms = 1 phút

        # Kiểm tra ngay lần đầu khi khởi động
        self.check_due_tasks()
        # ==========================================

    # ========================================================================
    # CÁC HÀM HỖ TRỢ GIAO DIỆN (STYLING HELPERS)
    # ========================================================================

    def _apply_theme(self):
        """
        Áp dụng stylesheet CSS cho toàn bộ ứng dụng.

        Kiểm tra xem theme đã được áp dụng chưa để tránh thêm nhiều lần.
        """
        app = QtWidgets.QApplication.instance()
        if app:
            current = app.styleSheet() or ""
            if "todo-theme" not in current:
                app.setStyleSheet(current + APP_STYLESHEET)

    def _create_card(self):
        """
        Tạo một QFrame với style "card" (khung bo góc đẹp).

        Returns:
            QFrame: Khung với style card
        """
        card = QtWidgets.QFrame()
        card.setObjectName("card")
        card.setFrameShape(QtWidgets.QFrame.NoFrame)
        card.setFrameShadow(QtWidgets.QFrame.Plain)
        return card

    def _make_chip(self, text, variant, *, compact=False):
        """
        Tạo một nhãn (label) dạng chip (huy hiệu) với màu sắc theo variant.

        Args:
            text (str): Nội dung hiển thị
            variant (str): Loại chip (ví dụ: "priority-high", "status-done")
            compact (bool): Chip nhỏ gọn hơn nếu True

        Returns:
            QLabel: Nhãn chip đã được tạo

        Các variant phổ biến:
        - "priority-high" (đỏ)
        - "priority-normal" (xanh dương)
        - "priority-low" (xanh lá)
        - "status-done" (xanh lá)
        - "status-todo" (vàng cam)
        """
        lbl = QtWidgets.QLabel(text)
        lbl.setObjectName("chip")
        lbl.setProperty("variant", variant)
        lbl.setProperty("compact", compact)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setMargin(0)
        return lbl

    def _refresh_widget_style(self, widget):
        """
        Làm mới style của widget và các widget con.

        Hàm này cần thiết khi thay đổi property động (ví dụ: done=True/False)
        để Qt áp dụng lại stylesheet.

        Args:
            widget: Widget cần làm mới style
        """
        if not widget:
            return
        style = widget.style()
        if style:
            style.unpolish(widget)  # Gỡ style cũ
            style.polish(widget)     # Áp dụng style mới

        # Làm mới cho tất cả widget con
        for child in widget.findChildren(QtWidgets.QWidget):
            c_style = child.style()
            if c_style:
                c_style.unpolish(child)
                c_style.polish(child)

    def _make_task_widget(self, it, *, dt=None, overdue=False):
        card = QtWidgets.QFrame()
        card.setObjectName("taskCard")
        card.setProperty("done", it.get("done", False))
        card.setProperty("selected", False)

        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        badge = QtWidgets.QLabel("✔" if it.get("done") else "⏳")
        badge.setObjectName("badge")
        badge.setProperty("done", it.get("done"))
        badge.setProperty("overdue", overdue)
        layout.addWidget(badge, 0, QtCore.Qt.AlignTop)

        body = QtWidgets.QVBoxLayout()
        body.setSpacing(8)
        body.setContentsMargins(0, 0, 0, 0)

        title = QtWidgets.QLabel(it.get("text", ""))
        title.setObjectName("taskTitle")
        title.setProperty("done", it.get("done"))
        title.setWordWrap(True)
        body.addWidget(title)

        chips = QtWidgets.QHBoxLayout()
        chips.setSpacing(8)

        priority = int(it.get("priority", 1))
        pr_variant = {2: "priority-high", 1: "priority-normal", 0: "priority-low"}.get(priority, "priority-normal")
        pr_text = {2: "Ưu tiên cao", 1: "Ưu tiên thường", 0: "Ưu tiên thấp"}.get(priority, "Ưu tiên")
        chips.addWidget(self._make_chip(pr_text, pr_variant, compact=True))

        status_variant = "status-done" if it.get("done") else "status-todo"
        status_text = "Đã hoàn thành" if it.get("done") else "Đang thực hiện"
        chips.addWidget(self._make_chip(status_text, status_variant, compact=True))

        if dt:
            # === SỬA DÒNG NÀY ===
            due_variant = "overdue" if overdue else "due"
            # ===================
            due_label = dt.strftime("Hạn: %d/%m %H:%M")
            chips.addWidget(self._make_chip(due_label, due_variant, compact=True))
        elif it.get("due_dt"):
            chips.addWidget(self._make_chip(f"Hạn: {it['due_dt']}", "due", compact=True))

        created = it.get("created_at")
        if created:
            created_date = created.split('T')[0] if 'T' in created else created
            chips.addWidget(self._make_chip(f"Tạo: {created_date}", "priority-normal", compact=True))

        chips.addStretch()
        body.addLayout(chips)

        note = it.get("note")
        if note:
            note_lbl = QtWidgets.QLabel(note)
            note_lbl.setObjectName("cardSubtitle")
            note_lbl.setWordWrap(True)
            note_lbl.setProperty("done", it.get("done"))
            body.addWidget(note_lbl)

        layout.addLayout(body, 1)

        self._refresh_widget_style(card)
        return card

    def _sync_task_selection(self):
        for i in range(self.list.count()):
            item = self.list.item(i)
            widget = self.list.itemWidget(item)
            if widget:
                widget.setProperty("selected", item.isSelected())
                self._refresh_widget_style(widget)

    def _update_statistics(self):
        total = len(self.store.items)
        done = sum(1 for x in self.store.items if x.get("done"))
        todo = total - done
        pct = int(done * 100 / total) if total else 0

        # === LOGIC MỚI ĐỂ ĐẾM QUÁ HẠN ===
        now = datetime.now()
        overdue_count = 0
        for it in self.store.items:
            # Chỉ đếm việc "chưa xong"
            if it.get("done"):
                continue
            
            dt = parse_dt(it.get("due_dt"))
            # Nếu có hạn chót VÀ hạn chót đã trôi qua
            if bool(dt and dt < now):
                overdue_count += 1
        # ==================================

        if hasattr(self, "stats_label"):
            self.stats_label.setText(f"{done}/{total} việc đã hoàn thành ({pct}%)" if total else "Chưa có việc nào")
        if hasattr(self, "header_progress"):
            self.header_progress.setMaximum(total if total else 1)
            self.header_progress.setValue(done)
            self.header_progress.setFormat(f"{pct}% hoàn thành" if total else "Chưa có công việc")
        
        if hasattr(self, "stat_total_chip"):
            self.stat_total_chip.setText(f"Tổng: {total}")
        if hasattr(self, "stat_todo_chip"):
            self.stat_todo_chip.setText(f"Đang làm: {todo}")
        if hasattr(self, "stat_done_chip"):
            self.stat_done_chip.setText(f"Hoàn thành: {done}")

        # === CẬP NHẬT CHO CHIP MỚI ===
        if hasattr(self, "stat_overdue_chip"):
            self.stat_overdue_chip.setText(f"Quá hạn: {overdue_count}")
            # Tự động ẩn nhãn đi nếu không có việc nào quá hạn
            self.stat_overdue_chip.setVisible(overdue_count > 0)
            self._refresh_widget_style(self.stat_overdue_chip)
        # ============================

        if hasattr(self, "stats_label"):
            # update window title as well
            self.setWindowTitle(f"Todo List — {done}/{total} ({pct}%)")

    # ---------------- Tab 1 ----------------
    def _build_tab_list(self):
        L = QtWidgets.QVBoxLayout(self.tab_list)
        L.setContentsMargins(24, 24, 24, 24)
        L.setSpacing(18)

        # Header card
        header_card = self._create_card()
        header_layout = QtWidgets.QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(12)
        info_box = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Quản lý công việc")
        title.setObjectName("cardTitle")
        subtitle = QtWidgets.QLabel("Sắp xếp mọi đầu việc mỗi ngày với giao diện trực quan.")
        subtitle.setObjectName("cardSubtitle")
        info_box.addWidget(title)
        info_box.addWidget(subtitle)
        info_box.addStretch()
        header_layout.addLayout(info_box)
        header_layout.addStretch()

        # === KHỐI CODE THÔNG BÁO ===
       
        bell_layout = QtWidgets.QHBoxLayout()
        bell_layout.setSpacing(4)
        bell_layout.setContentsMargins(0, 0, 0, 0)

        self.bell_button = QtWidgets.QPushButton("Thông báo")
        self.bell_button.setProperty("secondary", True) # Dùng style nút phụ
        self.bell_button.setToolTip("Thông báo")
        self.bell_button.clicked.connect(self.show_app_notifications) # Kết nối
        bell_layout.addWidget(self.bell_button)

        self.bell_counter = QtWidgets.QLabel("0")
        self.bell_counter.setObjectName("chip") # Tái sử dụng style của chip
        self.bell_counter.setProperty("variant", "priority-high") # Cho nó màu đỏ
        self.bell_counter.setToolTip("Số thông báo mới")
        self.bell_counter.setVisible(False) # Ẩn đi lúc đầu
        bell_layout.addWidget(self.bell_counter)
        
        header_layout.addLayout(bell_layout)
        header_layout.addSpacing(20) # Thêm khoảng cách với sidebar
        # ================================

        sidebar = QtWidgets.QVBoxLayout()
        sidebar.setSpacing(8)
        self.header_progress = QtWidgets.QProgressBar()
        self.header_progress.setFixedWidth(240)
        self.header_progress.setTextVisible(True)
        self.header_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.header_progress.setRange(0, 1)
        self.header_progress.setValue(0)
        self.header_progress.setFormat("Chưa có công việc")
        sidebar.addWidget(self.header_progress)
        self.stats_label = QtWidgets.QLabel("Chưa có việc")
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        sidebar.addWidget(self.stats_label)
        header_layout.addLayout(sidebar)
        L.addWidget(header_card)

        # Input card
        input_card = self._create_card()
        form = QtWidgets.QGridLayout(input_card)
        # ... (code input card giữ nguyên) ...
        form.setContentsMargins(24, 20, 24, 20)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        lbl = QtWidgets.QLabel("Công việc mới")
        lbl.setObjectName("cardSubtitle")
        form.addWidget(lbl, 0, 0, 1, 2)

        self.inp = QtWidgets.QLineEdit()
        self.inp.setPlaceholderText("Nhập nội dung công việc...")
        self.inp.setMinimumHeight(36)
        self.inp.returnPressed.connect(self.add_item)
        form.addWidget(self.inp, 1, 0, 1, 2)

        pr_lbl = QtWidgets.QLabel("Ưu tiên")
        pr_lbl.setObjectName("cardSubtitle")
        form.addWidget(pr_lbl, 0, 2)
        self.prio = QtWidgets.QComboBox()
        self.prio.addItem("Thấp", 0)
        self.prio.addItem("Thường", 1)
        self.prio.addItem("Cao", 2)
        self.prio.setCurrentIndex(1)
        self.prio.setMinimumWidth(140)
        form.addWidget(self.prio, 1, 2)

        btnAdd = QtWidgets.QPushButton("Thêm công việc")
        btnAdd.clicked.connect(self.add_item)
        form.addWidget(btnAdd, 1, 3)
        form.setColumnStretch(0, 3)
        form.setColumnStretch(1, 0)
        form.setColumnStretch(2, 1)
        form.setColumnStretch(3, 0)
        L.addWidget(input_card)


        # Filter card
        filter_card = self._create_card()
        filter_layout = QtWidgets.QGridLayout(filter_card)
        # ... (code filter card giữ nguyên) ...
        filter_layout.setContentsMargins(24, 20, 24, 20)
        filter_layout.setHorizontalSpacing(18)
        filter_layout.setVerticalSpacing(14)

        lbl_search = QtWidgets.QLabel("Tìm kiếm")
        lbl_search.setObjectName("cardSubtitle")
        filter_layout.addWidget(lbl_search, 0, 0)
        self.q = QtWidgets.QLineEdit()
        self.q.setPlaceholderText("Nhập từ khoá...")
        self.q.setClearButtonEnabled(True)
        self.q.textChanged.connect(self.refresh_all)
        filter_layout.addWidget(self.q, 1, 0)

        lbl_sort = QtWidgets.QLabel("Sắp xếp")
        lbl_sort.setObjectName("cardSubtitle")
        filter_layout.addWidget(lbl_sort, 0, 1)
        self.sort = QtWidgets.QComboBox()
        self.sort.addItem("Mặc định", "default")
        self.sort.addItem("Hạn chót", "due_dt")
        self.sort.addItem("Ưu tiên", "priority")
        self.sort.addItem("Ngày tạo", "created_at")
        self.sort.currentIndexChanged.connect(self.refresh_all)
        filter_layout.addWidget(self.sort, 1, 1)

        lbl_range = QtWidgets.QLabel("Phạm vi")
        lbl_range.setObjectName("cardSubtitle")
        filter_layout.addWidget(lbl_range, 0, 2)
        self.range = QtWidgets.QComboBox()
        self.range.addItem("Tất cả", "all")
        self.range.addItem("Hôm nay", "today")
        self.range.addItem("Trong tuần", "week")
        self.range.currentIndexChanged.connect(self.refresh_all)
        filter_layout.addWidget(self.range, 1, 2)

        status_lbl = QtWidgets.QLabel("Trạng thái")
        status_lbl.setObjectName("cardSubtitle")
        filter_layout.addWidget(status_lbl, 0, 3)
        radio_row = QtWidgets.QHBoxLayout()
        radio_row.setSpacing(12)
        self.filter = QtWidgets.QButtonGroup(self)
        rbAll = QtWidgets.QRadioButton("Tất cả")
        rbTodo = QtWidgets.QRadioButton("Chưa xong")
        rbDone = QtWidgets.QRadioButton("Đã xong")
        rbAll.setChecked(True)
        for i, rb in enumerate([rbAll, rbTodo, rbDone]):
            rb.toggled.connect(self.refresh_all)
            self.filter.addButton(rb, i)
            radio_row.addWidget(rb)
        radio_row.addStretch()
        filter_layout.addLayout(radio_row, 1, 3)
        filter_layout.setColumnStretch(0, 1)
        filter_layout.setColumnStretch(1, 1)
        filter_layout.setColumnStretch(2, 1)
        filter_layout.setColumnStretch(3, 2)
        L.addWidget(filter_card)


        # List card
        list_card = self._create_card()
        list_layout = QtWidgets.QVBoxLayout(list_card)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_layout.setSpacing(14)

        list_title = QtWidgets.QLabel("Danh sách công việc")
        list_title.setObjectName("cardTitle")
        list_layout.addWidget(list_title)

        # === KHỐI CODE NÀY ĐÃ ĐƯỢC SỬA ===
        chips_row = QtWidgets.QHBoxLayout()
        chips_row.setSpacing(12)
        
        self.stat_total_chip = self._make_chip("Tổng: 0", "priority-normal")
        self.stat_todo_chip = self._make_chip("Đang làm: 0", "status-todo")
        self.stat_done_chip = self._make_chip("Hoàn thành: 0", "status-done")
        
        # Dòng mới được thêm vào
        self.stat_overdue_chip = self._make_chip("Quá hạn: 0", "priority-high") 
        
        chips_row.addWidget(self.stat_total_chip)
        chips_row.addWidget(self.stat_todo_chip)
        chips_row.addWidget(self.stat_done_chip)
        chips_row.addWidget(self.stat_overdue_chip) # Thêm chip mới vào layout
        
        chips_row.addStretch()
        list_layout.addLayout(chips_row)
        # =================================

        self.list = QtWidgets.QListWidget()
        self.list.setObjectName("taskList")
        # ... (code list widget giữ nguyên) ...
        self.list.setAlternatingRowColors(False)
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list.setSpacing(10)
        self.list.setWordWrap(True)
        self.list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list.setUniformItemSizes(False)
        self.list.itemSelectionChanged.connect(self._sync_task_selection)
        self.list.itemDoubleClicked.connect(lambda *_: self.edit_item())


        self.list_stack = QtWidgets.QStackedLayout()
        self.list_stack.addWidget(self.list)
        # ... (code list stack giữ nguyên) ...
        self.list_placeholder = QtWidgets.QLabel("Chưa có công việc nào. Hãy thêm việc mới để bắt đầu!")
        self.list_placeholder.setObjectName("placeholder")
        self.list_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.list_placeholder.setWordWrap(True)
        placeholder_wrap = QtWidgets.QWidget()
        placeholder_layout = QtWidgets.QVBoxLayout(placeholder_wrap)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self.list_placeholder)
        placeholder_layout.addStretch()
        self.list_stack.addWidget(placeholder_wrap)
        list_container = QtWidgets.QWidget()
        list_container.setLayout(self.list_stack)
        list_layout.addWidget(list_container, 1)


        style = self.style()
        btnDone = QtWidgets.QPushButton("Hoàn thành")
        # ... (code các nút bấm giữ nguyên) ...
        btnDone.setIcon(style.standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        btnDone.clicked.connect(self.toggle_done)

        btnEdit = QtWidgets.QPushButton("Sửa")
        btnEdit.setIcon(style.standardIcon(QtWidgets.QStyle.SP_FileDialogContentsView))
        btnEdit.setProperty("secondary", True)
        btnEdit.clicked.connect(self.edit_item)

        btnDel = QtWidgets.QPushButton("Xoá")
        btnDel.setIcon(style.standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        btnDel.setProperty("danger", True)
        btnDel.clicked.connect(self.delete_item)

        btnUndo = QtWidgets.QPushButton("Hoàn tác")
        btnUndo.setIcon(style.standardIcon(QtWidgets.QStyle.SP_ArrowBack))
        btnUndo.setProperty("secondary", True)
        btnUndo.clicked.connect(self.undo)

        btnUp = QtWidgets.QPushButton("Lên")
        btnUp.setIcon(style.standardIcon(QtWidgets.QStyle.SP_ArrowUp))
        btnUp.setProperty("secondary", True)
        btnUp.clicked.connect(self.move_up)

        btnDown = QtWidgets.QPushButton("Xuống")
        btnDown.setIcon(style.standardIcon(QtWidgets.QStyle.SP_ArrowDown))
        btnDown.setProperty("secondary", True)
        btnDown.clicked.connect(self.move_down)

        actions_bar = QtWidgets.QHBoxLayout()
        actions_bar.setSpacing(12)
        actions_bar.addWidget(btnDone)
        actions_bar.addWidget(btnEdit)
        actions_bar.addWidget(btnDel)
        actions_bar.addWidget(btnUndo)
        actions_bar.addStretch()
        actions_bar.addWidget(btnUp)
        actions_bar.addWidget(btnDown)
        list_layout.addLayout(actions_bar)

        L.addWidget(list_card, 1)

        # Shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self, self.delete_item)
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, self.toggle_done)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self, self.undo)

    # ---------------- Tab 2 ----------------
    def _build_tab_day(self):
        L = QtWidgets.QVBoxLayout(self.tab_day)
        L.setContentsMargins(24, 24, 24, 24)
        L.setSpacing(18)

        day_card = self._create_card()
        card_layout = QtWidgets.QVBoxLayout(day_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        head = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Công việc trong ngày")
        title.setObjectName("cardTitle")
        head.addWidget(title)
        head.addStretch()
        head.addWidget(QtWidgets.QLabel("Ngày"))
        self.day_sel = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.day_sel.setDisplayFormat(QT_D_FMT)
        self.day_sel.setCalendarPopup(True)
        self.day_sel.setFixedWidth(140)
        self.day_sel.dateChanged.connect(lambda *_: self.refresh_day())
        head.addWidget(self.day_sel)
        btnToday = QtWidgets.QPushButton("Hôm nay")
        btnToday.setProperty("secondary", True)
        btnToday.clicked.connect(self._set_day_today)
        head.addWidget(btnToday)
        self.day_count_label = QtWidgets.QLabel("0 việc")
        self.day_count_label.setObjectName("cardSubtitle")
        head.addSpacing(12)
        head.addWidget(self.day_count_label)
        card_layout.addLayout(head)

        self.day_tbl = QtWidgets.QTableWidget(0, 4)
        self.day_tbl.setHorizontalHeaderLabels(["GIỜ","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"])
        self.day_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.day_tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.day_tbl.setAlternatingRowColors(True)
        self.day_tbl.verticalHeader().setVisible(False)
        header = self.day_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.day_tbl.setWordWrap(True)
        self.day_tbl.setShowGrid(False)
        card_layout.addWidget(self.day_tbl)
        L.addWidget(day_card, 1)

    # ---------------- Tab 3 ----------------
    def _build_tab_week(self):
        L = QtWidgets.QVBoxLayout(self.tab_week)
        L.setContentsMargins(24, 24, 24, 24)
        L.setSpacing(18)

        week_card = self._create_card()
        card_layout = QtWidgets.QVBoxLayout(week_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        head = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Công việc trong tuần")
        title.setObjectName("cardTitle")
        head.addWidget(title)
        head.addStretch()
        head.addWidget(QtWidgets.QLabel("Tuần chứa ngày"))
        self.week_anchor = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.week_anchor.setDisplayFormat(QT_D_FMT)
        self.week_anchor.setCalendarPopup(True)
        self.week_anchor.setFixedWidth(140)
        self.week_anchor.dateChanged.connect(lambda *_: self.refresh_week())
        head.addWidget(self.week_anchor)
        btnThis = QtWidgets.QPushButton("Tuần này")
        btnThis.setProperty("secondary", True)
        btnThis.clicked.connect(self._set_week_this)
        head.addWidget(btnThis)
        self.week_count_label = QtWidgets.QLabel("0 việc")
        self.week_count_label.setObjectName("cardSubtitle")
        head.addSpacing(12)
        head.addWidget(self.week_count_label)
        card_layout.addLayout(head)

        self.week_tbl = QtWidgets.QTableWidget(0, 6)
        self.week_tbl.setHorizontalHeaderLabels(["THỨ","NGÀY","GIỜ","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"])
        self.week_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.week_tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.week_tbl.setAlternatingRowColors(True)
        self.week_tbl.verticalHeader().setVisible(False)
        header = self.week_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.week_tbl.setWordWrap(True)
        self.week_tbl.setShowGrid(False)
        card_layout.addWidget(self.week_tbl)
        L.addWidget(week_card, 1)
    # ---------------- Tab 4 ----------------
    def _build_tab_overdue(self):
        """Xây dựng giao diện cho Tab 4 (Quá hạn)."""
        L = QtWidgets.QVBoxLayout(self.tab_overdue)
        L.setContentsMargins(24, 24, 24, 24)
        L.setSpacing(18)

        card = self._create_card()
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        # Header (chỉ có Tiêu đề và Nhãn đếm)
        head = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Công việc quá hạn")
        title.setObjectName("cardTitle")
        head.addWidget(title)
        head.addStretch()
        
        # Nhãn đếm số việc quá hạn
        self.overdue_count_label = QtWidgets.QLabel("0 việc")
        self.overdue_count_label.setObjectName("cardSubtitle")
        head.addSpacing(12)
        head.addWidget(self.overdue_count_label)
        card_layout.addLayout(head)

        # Bảng (Table) hiển thị công việc
        self.overdue_tbl = QtWidgets.QTableWidget(0, 4) # 0 hàng, 4 cột
        self.overdue_tbl.setHorizontalHeaderLabels(["HẠN CHÓT","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"])
        
        self.overdue_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.overdue_tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.overdue_tbl.setAlternatingRowColors(True)
        self.overdue_tbl.verticalHeader().setVisible(False)
        
        header = self.overdue_tbl.horizontalHeader()
        # Chế độ co giãn cột
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # Cột HẠN CHÓT
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)           # Cột NỘI DUNG
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents) # Cột ƯU TIÊN
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents) # Cột TRẠNG THÁI
        
        self.overdue_tbl.setWordWrap(True)
        self.overdue_tbl.setShowGrid(False)
        card_layout.addWidget(self.overdue_tbl)
        L.addWidget(card, 1)

    # ========================================================================
    # CÁC HÀM CRUD - THÊM, SỬA, XÓA CÔNG VIỆC
    # ========================================================================

    def add_item(self):
        """
        Thêm công việc mới vào danh sách.

        Quy trình:
        1. Lấy nội dung từ ô nhập liệu
        2. Hiển thị dialog để nhập đầy đủ thông tin
        3. Thêm vào store và lưu file
        4. Làm mới giao diện
        """
        text = self.inp.text().strip()
        base_priority = self.prio.currentData()
        if base_priority is None:
            base_priority = self.prio.currentIndex()

        # Mở dialog thêm công việc
        dialog = TaskDialog(
            self,
            title="Thêm công việc",
            task={"text": text, "priority": base_priority}
        )

        # Nếu có nội dung sẵn, bôi đen để dễ sửa
        if text:
            dialog.text_edit.selectAll()

        # Nếu người dùng hủy, không làm gì
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return

        # Lấy dữ liệu từ dialog và thêm vào store
        data = dialog.get_data()
        self.store.items.append({
            "text": data["text"],
            "done": False,
            "priority": data["priority"],
            "due_dt": data.get("due_dt"),
            "note": data.get("note"),
            "created_at": now_iso(),
            "done_at": None
        })

        # Xóa ô nhập và làm mới giao diện
        self.inp.clear()
        self.refresh_all()
        self.store.save()

    def _current_index(self):
        """
        Lấy chỉ số (index) thực của công việc đang chọn trong danh sách đã lọc.

        Returns:
            int hoặc None: Index trong self.store.items, hoặc None nếu không chọn gì

        Lưu ý: Vì danh sách có thể bị lọc, nên index hiển thị khác với index thật.
        """
        row = self.list.currentRow()
        if row < 0:
            return None

        # Lấy mapping từ danh sách đã lọc sang index thật
        mapping = self._filtered_indices()
        if 0 <= row < len(mapping):
            return mapping[row]
        return None

    def edit_item(self):
        """
        Chỉnh sửa công việc đang được chọn.

        Quy trình:
        1. Lấy index của công việc đang chọn
        2. Hiển thị dialog với dữ liệu hiện tại
        3. Cập nhật dữ liệu và lưu file
        4. Làm mới giao diện
        """
        idx = self._current_index()
        if idx is None:
            return

        it = self.store.items[idx]

        # Mở dialog sửa công việc
        dialog = TaskDialog(self, title="Cập nhật công việc", task=it)

        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return

        # Cập nhật dữ liệu
        data = dialog.get_data()
        it["text"] = data["text"]
        it["priority"] = data["priority"]
        it["due_dt"] = data.get("due_dt")
        it["note"] = data.get("note")
        it["notified"] = False  # Reset để có thể thông báo lại

        self.refresh_all()
        self.store.save()

    def delete_item(self):
        """
        Xóa công việc đang được chọn.

        Quy trình:
        1. Xác nhận với người dùng
        2. Lưu trạng thái để có thể hoàn tác
        3. Xóa khỏi store và lưu file
        4. Làm mới giao diện
        """
        idx = self._current_index()
        if idx is None:
            return

        # Xác nhận xóa
        if QtWidgets.QMessageBox.question(
            self, "Xoá", "Xoá công việc đã chọn?"
        ) != QtWidgets.QMessageBox.Yes:
            return

        # Lưu để có thể hoàn tác
        self._undo = ("del", idx, dict(self.store.items[idx]))

        # Xóa khỏi danh sách
        del self.store.items[idx]

        self.refresh_all()
        self.store.save()

    def undo(self):
        """
        Hoàn tác thao tác xóa gần nhất.

        Chỉ hỗ trợ hoàn tác 1 lần.
        """
        if not self._undo:
            return

        kind, idx, payload = self._undo

        if kind == "del":
            # Chèn lại vào vị trí cũ (hoặc cuối nếu vượt quá)
            idx = min(idx, len(self.store.items))
            self.store.items.insert(idx, payload)

        self._undo = None
        self.refresh_all()
        self.store.save()

    def toggle_done(self):
        """
        Đánh dấu công việc đang chọn là hoàn thành/chưa hoàn thành.

        Khi đánh dấu hoàn thành:
        - done = True
        - done_at = thời gian hiện tại

        Khi bỏ đánh dấu:
        - done = False
        - done_at = None
        - notified = False (để có thể thông báo lại)
        """
        idx = self._current_index()
        if idx is None:
            return

        it = self.store.items[idx]
        it["done"] = not it["done"]
        it["done_at"] = now_iso() if it["done"] else None

        # Reset trạng thái thông báo nếu đánh dấu chưa xong
        if not it["done"]:
            it["notified"] = False

        self.refresh_all()
        self.store.save()

    # ---------------- Filter + Sort ----------------
    def _is_today(self, it):
        dt = parse_dt(it.get("due_dt"))
        return bool(dt and dt.date() == date.today())

    def _is_in_week(self, it, anchor=None):
        dt = parse_dt(it.get("due_dt"))
        if not dt:
            return False
        a = anchor or date.today()
        return start_of_week(a) <= dt.date() <= end_of_week(a)

    def _filtered_indices(self):
        q = self.q.text().lower()
        mode = ["all", "todo", "done"][self.filter.checkedId()]
        rng = self.range.currentData() or "all"
        idxs = []
        for i, it in enumerate(self.store.items):
            if mode == "todo" and it["done"]:
                continue
            if mode == "done" and not it["done"]:
                continue
            if rng == "today" and not self._is_today(it):
                continue
            if rng == "week" and not self._is_in_week(it):
                continue
            if q and q not in it["text"].lower():
                continue
            idxs.append(i)
        key = self.sort.currentData() or "default"
        if key == "due_dt":
            idxs.sort(key=lambda i: (self.store.items[i]["due_dt"] is None,
                                     self.store.items[i]["due_dt"] or "9999-12-31 23:59"))
        elif key == "priority":
            idxs.sort(key=lambda i: -int(self.store.items[i].get("priority", 1)))
        elif key == "created_at":
            idxs.sort(key=lambda i: self.store.items[i].get("created_at", ""), reverse=True)
        return idxs

    def refresh_list(self):
        self.list.blockSignals(True)
        try:
            self.list.clear()
            now = datetime.now()  # <-- Dòng này đúng
            
            filtered = self._filtered_indices()
            for idx in filtered:
                it = self.store.items[idx]
                dt = parse_dt(it.get("due_dt")) if it.get("due_dt") else None
                
                # === SỬA DÒNG NÀY ===
                overdue = bool(dt and dt < now and not it.get("done")) # So sánh với 'now'
                # ===================

                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, idx)
                pr = int(it.get("priority", 1))
                pr_txt = {0: "Thấp", 1: "Thường", 2: "Cao"}.get(pr, "Thường")
                due_txt = dt.strftime("%d/%m %H:%M") if dt else "Không hạn"
                tooltip_lines = [f"Ưu tiên: {pr_txt}", f"Hạn chót: {due_txt}"]
                
                # === SỬA DÒNG NÀY (bỏ 'not it.get("done")') ===
                if overdue: # Biến overdue đã bao gồm logic "chưa xong"
                # ============================================
                    tooltip_lines.append("Trạng thái: Quá hạn")
                
                note = it.get("note")
                if note:
                    tooltip_lines.append(f"Ghi chú: {note}")
                
                item.setToolTip("\n".join(tooltip_lines))
                widget = self._make_task_widget(it, dt=dt, overdue=overdue)
                size = widget.sizeHint()
                # Bạn đã tăng size lên 120, rất tốt!
                item.setSizeHint(QtCore.QSize(0, max(size.height(), 120))) 
                self.list.addItem(item)
                self.list.setItemWidget(item, widget)
        finally:
            self.list.blockSignals(False)
        self._sync_task_selection()
        self._update_statistics()
        self._update_list_placeholder()

    def _update_list_placeholder(self):
        if not hasattr(self, "list_stack"):
            return
        if self.list.count():
            self.list_stack.setCurrentIndex(0)
        else:
            if self.store.items:
                self.list_placeholder.setText("Không tìm thấy công việc phù hợp với bộ lọc hiện tại.")
            else:
                self.list_placeholder.setText("Chưa có công việc nào. Hãy thêm việc mới để bắt đầu!")
            self.list_stack.setCurrentIndex(1)

    def _update_title(self):
        self._update_statistics()

    # ---------------- Move ----------------
    def _can_move_linear(self):
        return (self.filter.checkedId() == 0 and
                not self.q.text().strip() and
                (self.sort.currentData() or "default") == "default" and
                (self.range.currentData() or "all") == "all")

    def move_up(self):
        if not self._can_move_linear():
            QtWidgets.QMessageBox.information(self, "Không thể di chuyển",
                "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self._current_index()
        if idx is None or idx <= 0:
            return
        self.store.items[idx - 1], self.store.items[idx] = self.store.items[idx], self.store.items[idx - 1]
        self.refresh_list()
        self.list.setCurrentRow(idx - 1)
        self.store.save()

    def move_down(self):
        if not self._can_move_linear():
            QtWidgets.QMessageBox.information(self, "Không thể di chuyển",
                "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self._current_index()
        if idx is None or idx >= len(self.store.items) - 1:
            return
        self.store.items[idx + 1], self.store.items[idx] = self.store.items[idx], self.store.items[idx + 1]
        self.refresh_list()
        self.list.setCurrentRow(idx + 1)
        self.store.save()

    # ---------------- Day view ----------------
    def _set_day_today(self):
        self.day_sel.setDate(QtCore.QDate.currentDate())

    def refresh_day(self):
        d = self.day_sel.date().toPyDate()
        now = datetime.now() # Lấy thời gian hiện tại
        
        rows = []
        for it in self.store.items:
            dt = parse_dt(it.get("due_dt"))
            if dt and dt.date() == d:
                # Kiểm tra xem có quá hạn không
                is_overdue = (dt < now and not it.get("done"))
                rows.append((dt, it, is_overdue)) # Truyền trạng thái quá hạn
                
        rows.sort(key=lambda x: x[0])
        self.day_tbl.setRowCount(0)
        
        for dt, it, is_overdue in rows: # Lấy is_overdue
            r = self.day_tbl.rowCount()
            self.day_tbl.insertRow(r)
            
            # === LOGIC TRẠNG THÁI MỚI ===
            status_text = "Đã xong"
            if not it.get("done"):
                status_text = "Quá hạn" if is_overdue else "Chưa xong"
            # ============================

            vals = [dt.strftime("%H:%M"), it["text"],
                    {0: "Thấp", 1: "Thường", 2: "Cao"}.get(int(it.get("priority", 1)), "Thường"),
                    status_text] # Dùng status_text mới
            
            for c, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                if c == 1:
                    item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    note = it.get("note")
                    if note:
                        item.setToolTip(note)
                else:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                
                # === THÊM MÀU SẮC CHO TRẠNG THÁI ===
                if is_overdue and c == 3: # Cột Trạng thái (index 3)
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#e03131"))) # Màu đỏ
                elif it.get("done") and c == 3:
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#2b8a3e"))) # Màu xanh lá
                # =================================
                
                self.day_tbl.setItem(r, c, item)
                
        self.day_tbl.resizeRowsToContents()
        self.day_count_label.setText(f"{len(rows)} việc" if rows else "Không có việc")
    # ---------------- Week view ----------------
    def _set_week_this(self):
        self.week_anchor.setDate(QtCore.QDate.currentDate())

    def refresh_week(self):
        anchor = self.week_anchor.date().toPyDate()
        monday, sunday = start_of_week(anchor), end_of_week(anchor)
        now = datetime.now() # Lấy thời gian hiện tại
        
        rows = []
        for it in self.store.items:
            dt = parse_dt(it.get("due_dt"))
            if dt and monday <= dt.date() <= sunday:
                # Kiểm tra xem có quá hạn không
                is_overdue = (dt < now and not it.get("done"))
                rows.append((dt, it, is_overdue)) # Truyền trạng thái quá hạn
                
        rows.sort(key=lambda x: (x[0].date(), x[0].time()))
        self.week_tbl.setRowCount(0)
        
        for dt, it, is_overdue in rows: # Lấy is_overdue
            r = self.week_tbl.rowCount()
            self.week_tbl.insertRow(r)
            
            # === LOGIC TRẠNG THÁI MỚI ===
            status_text = "Đã xong"
            if not it.get("done"):
                status_text = "Quá hạn" if is_overdue else "Chưa xong"
            # ============================

            vals = [WEEKDAY_VN[dt.weekday()], dt.strftime(D_FMT), dt.strftime("%H:%M"),
                    it["text"], {0: "Thấp", 1: "Thường", 2: "Cao"}.get(int(it.get("priority", 1)), "Thường"),
                    status_text] # Dùng status_text mới
            
            for c, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                if c in (3,):
                    item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    note = it.get("note")
                    if note:
                        item.setToolTip(note)
                else:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                
                # === THÊM MÀU SẮC CHO TRẠNG THÁI ===
                if is_overdue and c == 5: # Cột Trạng thái (index 5)
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#e03131"))) # Màu đỏ
                elif it.get("done") and c == 5:
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#2b8a3e"))) # Màu xanh lá
                # =================================
                
                self.week_tbl.setItem(r, c, item)
                
        self.week_tbl.resizeRowsToContents()
        self.week_count_label.setText(f"{len(rows)} việc" if rows else "Không có việc")
    # ---------------- Overdue view ----------------
    def refresh_overdue(self):
        """Làm mới QTableWidget ở Tab 4 (Quá hạn)."""
        now = datetime.now() # Lấy thời gian hiện tại
        
        rows = [] # Danh sách các hàng (row)
        
        # Lọc các công việc
        for it in self.store.items:
            # Bỏ qua nếu việc đã xong
            if it.get("done"):
                continue
                
            dt = parse_dt(it.get("due_dt"))
            
            # Đây chính là logic tìm việc quá hạn:
            # (Có hạn chót) VÀ (hạn chót < bây giờ)
            if dt and dt < now:
                # Lưu lại (datetime, item, is_overdue=True)
                rows.append((dt, it, True))
                
        # Sắp xếp theo hạn chót (cũ nhất, quá hạn lâu nhất lên đầu)
        rows.sort(key=lambda x: x[0])
        self.overdue_tbl.setRowCount(0) # Xoá bảng cũ
        
        # Thêm lại dữ liệu vào bảng
        for dt, it, is_overdue in rows:
            r = self.overdue_tbl.rowCount()
            self.overdue_tbl.insertRow(r)
            
            # Giá trị cho 4 cột: ["HẠN CHÓT","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"]
            vals = [
                dt.strftime("%d/%m/%Y %H:%M"), # Hiển thị đầy đủ ngày giờ
                it["text"],
                {0: "Thấp", 1: "Thường", 2: "Cao"}.get(int(it.get("priority", 1)), "Thường"),
                "Quá hạn" # Trạng thái luôn là "Quá hạn"
            ]
            
            for c, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                
                # Căn lề
                if c == 1: # Cột Nội dung
                    item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    note = it.get("note")
                    if note:
                        item.setToolTip(note) # Thêm tooltip ghi chú
                else:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                
                # Thêm màu đỏ cho cột HẠN CHÓT (c=0) và TRẠNG THÁI (c=3)
                if c == 0 or c == 3:
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#e03131"))) # Màu đỏ
                
                self.overdue_tbl.setItem(r, c, item)
                
        self.overdue_tbl.resizeRowsToContents() # Tự động điều chỉnh chiều cao hàng
        
        # Cập nhật nhãn đếm
        self.overdue_count_label.setText(f"{len(rows)} việc" if rows else "Không có việc")


    def refresh_all(self):
        self.refresh_list()
        self.refresh_day()
        self.refresh_week()
        self.refresh_overdue() # <-- THÊM DÒNG NÀY

    # ========================================================================
    # HỆ THỐNG THÔNG BÁO (NOTIFICATION SYSTEM)
    # ========================================================================

    def show_notification(self, title, message):
        """
        Hiển thị thông báo qua system tray (vùng thông báo Windows).

        Args:
            title (str): Tiêu đề thông báo
            message (str): Nội dung thông báo

        Thông báo sẽ xuất hiện ở góc màn hình trong 3 giây.
        """
        if self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QtWidgets.QSystemTrayIcon.Information,
                3000  # Thông báo hiển thị trong 3 giây
            )

    def check_due_tasks(self):
        """
        Kiểm tra các công việc đến hạn và gửi thông báo.

        Hàm này được QTimer gọi tự động mỗi 1 phút.

        Quy trình:
        1. Duyệt qua tất cả công việc
        2. Tìm các việc chưa xong, chưa thông báo, đã đến hạn
        3. Gửi thông báo system tray
        4. Thêm vào danh sách thông báo trong app
        5. Đánh dấu là đã thông báo
        """
        if not self.tray_icon:
            return  # Không làm gì nếu không có system tray

        now = datetime.now()
        tasks_to_notify = []

        # Tìm các công việc cần thông báo
        for task in self.store.items:
            # Bỏ qua nếu: Đã xong HOẶC đã thông báo rồi
            if task.get("done") or task.get("notified"):
                continue

            due_str = task.get("due_dt")
            if not due_str:
                continue

            due_dt = parse_dt(due_str)
            if not due_dt:
                continue

            # Nếu công việc đã (hoặc đang) đến hạn
            if due_dt <= now:
                tasks_to_notify.append(task)

        # Nếu có công việc cần thông báo
        if tasks_to_notify:
            # Đánh dấu tất cả là "đã thông báo"
            for task in tasks_to_notify:
                task["notified"] = True

            # Tạo nội dung thông báo system tray
            if len(tasks_to_notify) == 1:
                title = "Công việc đến hạn!"
                message = tasks_to_notify[0].get("text")
            else:
                title = f"{len(tasks_to_notify)} công việc đến hạn!"
                message = f"Việc đầu tiên: {tasks_to_notify[0].get('text')}"

            # Hiển thị thông báo system tray
            self.show_notification(title, message)

            # Thêm vào danh sách thông báo trong app
            for task in tasks_to_notify:
                msg = f"Đến hạn: {task.get('text')}"
                if msg not in self.app_notifications:
                    self.app_notifications.append(msg)

            # Cập nhật số đếm trên icon chuông
            if hasattr(self, "bell_counter"):
                self.update_bell_counter()

            # Lưu lại thay đổi (đánh dấu notified=True)
            self.store.save()

    def update_bell_counter(self):
        """
        Cập nhật số đếm trên biểu tượng chuông.

        - Nếu có thông báo: Hiển thị số lượng
        - Nếu không có: Ẩn số đếm
        """
        count = len(self.app_notifications)
        if count > 0:
            self.bell_counter.setText(str(count))
            self.bell_counter.setVisible(True)
        else:
            self.bell_counter.setVisible(False)

        # Làm mới style
        self._refresh_widget_style(self.bell_counter)
        self._refresh_widget_style(self.bell_button)

    def show_app_notifications(self):
        """
        Hiển thị menu pop-up chứa các thông báo.

        Menu sẽ hiện ra bên dưới nút chuông với:
        - Danh sách các thông báo (không thể click)
        - Nút "Đánh dấu đã đọc (Xoá tất cả)"
        """
        if not self.app_notifications:
            QtWidgets.QMessageBox.information(
                self, "Thông báo", "Không có thông báo mới."
            )
            return

        menu = QtWidgets.QMenu(self)

        # Thêm các thông báo vào menu
        for msg in self.app_notifications:
            action = QtWidgets.QAction(msg, self)
            action.setEnabled(False)  # Chỉ để hiển thị, không bấm được
            menu.addAction(action)

        menu.addSeparator()

        # Thêm hành động "Xoá tất cả"
        clear_action = QtWidgets.QAction("✔️ Đánh dấu đã đọc (Xoá tất cả)", self)
        clear_action.triggered.connect(self.clear_app_notifications)
        menu.addAction(clear_action)

        # Hiển thị menu ngay bên dưới nút chuông
        menu.exec_(self.bell_button.mapToGlobal(
            QtCore.QPoint(0, self.bell_button.height())
        ))

    def clear_app_notifications(self):
        """
        Xoá tất cả thông báo và cập nhật icon chuông.

        Lưu ý: Khi khởi động lại app, thông báo có thể xuất hiện lại
        nếu công việc vẫn quá hạn.
        """
        self.app_notifications.clear()
        self.update_bell_counter()        



# ============================================================================
# HÀM MAIN - ĐIỂM KHỞI ĐỘNG CHƯƠNG TRÌNH
# ============================================================================

def main():
    """
    Hàm khởi động ứng dụng.

    Quy trình:
    1. Tạo QApplication (ứng dụng Qt)
    2. Thiết lập font mặc định
    3. Tạo cửa sổ chính (Main)
    4. Hiển thị cửa sổ
    5. Bắt đầu vòng lặp sự kiện (event loop)
    """
    app = QtWidgets.QApplication(sys.argv)

    # Thiết lập font mặc định cho toàn bộ ứng dụng
    default_font = QtGui.QFont("Segoe UI", 9)
    app.setFont(default_font)

    # Tạo và hiển thị cửa sổ chính
    w = Main()
    w.show()

    # Bắt đầu vòng lặp sự kiện và thoát khi đóng ứng dụng
    sys.exit(app.exec_())


# Điểm vào chương trình
if __name__ == "__main__":
    main()