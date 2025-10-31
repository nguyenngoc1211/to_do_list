#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, shutil, sys
from datetime import datetime, date, timedelta

from PyQt5 import QtWidgets, QtCore, QtGui


DATA_FILE = "todos.json"
DT_FMT = "%Y-%m-%d %H:%M"   # 24h
D_FMT  = "%Y-%m-%d"
WEEKDAY_VN = ["Th 2","Th 3","Th 4","Th 5","Th 6","Th 7","CN"]

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())
def end_of_week(d: date) -> date:
    return start_of_week(d) + timedelta(days=6)

def parse_dt(s):
    try:
        return datetime.strptime(s, DT_FMT) if s else None
    except Exception:
        return None

class Store:
    def __init__(self, path):
        self.path = path
        self.items = []

    def migrate(self, it):
        it = dict(it) if isinstance(it, dict) else {"text": str(it)}
        it.setdefault("text", "")
        it.setdefault("done", False)
        it.setdefault("priority", 1)          # 0 thấp, 1 thường, 2 cao
        if "due_dt" not in it:
            due = it.get("due")               # nâng cấp từ bản cũ
            it["due_dt"] = f"{due} 23:59" if due else None
        it.pop("due", None)
        it.setdefault("created_at", now_iso())
        it.setdefault("done_at", None)
        return it

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.items = [self.migrate(x) for x in (raw if isinstance(raw, list) else [])]
            except Exception:
                self.items = []
        else:
            self.items = []

    def save(self):
        try:
            if os.path.exists(self.path):
                shutil.copyfile(self.path, self.path + ".bak")
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Lỗi lưu", str(e))

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")
        self.resize(980, 620)

        self.store = Store(DATA_FILE)
        self.store.load()
        self._undo = None

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # ==== Tab 1: Danh sách ====
        self.tab_list = QtWidgets.QWidget()
        tabs.addTab(self.tab_list, "Danh sách")
        self._build_tab_list()

        # ==== Tab 2: Trong ngày ====
        self.tab_day = QtWidgets.QWidget()
        tabs.addTab(self.tab_day, "Trong ngày")
        self._build_tab_day()

        # ==== Tab 3: Trong tuần ====
        self.tab_week = QtWidgets.QWidget()
        tabs.addTab(self.tab_week, "Trong tuần")
        self._build_tab_week()

        self.refresh_all()

    # ---------------- Tab 1 ----------------
    def _build_tab_list(self):
        L = QtWidgets.QVBoxLayout(self.tab_list)

        # Top input
        top = QtWidgets.QHBoxLayout()
        self.inp = QtWidgets.QLineEdit()
        self.inp.setPlaceholderText("Nhập công việc...")
        self.inp.returnPressed.connect(self.add_item)
        top.addWidget(self.inp)

        btnAdd = QtWidgets.QPushButton("Thêm (Enter)")
        btnAdd.clicked.connect(self.add_item)
        top.addWidget(btnAdd)

        labPr = QtWidgets.QLabel("Ưu tiên")
        top.addWidget(labPr)
        self.prio = QtWidgets.QComboBox()
        self.prio.addItems(["0","1","2"])
        self.prio.setCurrentIndex(1)
        self.prio.setFixedWidth(60)
        top.addWidget(self.prio)

        L.addLayout(top)

        # Tools
        tools = QtWidgets.QHBoxLayout()
        tools.addWidget(QtWidgets.QLabel("Tìm"))
        self.q = QtWidgets.QLineEdit()
        self.q.setFixedWidth(200)
        self.q.textChanged.connect(self.refresh_all)
        tools.addWidget(self.q)

        tools.addWidget(QtWidgets.QLabel("Sắp xếp"))
        self.sort = QtWidgets.QComboBox()
        self.sort.addItems(["default","due_dt","priority","created_at"])
        self.sort.currentTextChanged.connect(self.refresh_all)
        tools.addWidget(self.sort)

        tools.addWidget(QtWidgets.QLabel("Phạm vi"))
        self.range = QtWidgets.QComboBox()
        self.range.addItems(["all","today","week"])
        self.range.currentTextChanged.connect(self.refresh_all)
        tools.addStretch()
        L.addLayout(tools)

        # List
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        L.addWidget(self.list)

        # Bottom actions
        bot = QtWidgets.QHBoxLayout()
        btnDone = QtWidgets.QPushButton("Hoàn thành")
        btnDone.clicked.connect(self.toggle_done)
        btnEdit = QtWidgets.QPushButton("Sửa")
        btnEdit.clicked.connect(self.edit_item)
        btnDel = QtWidgets.QPushButton("Xoá")
        btnDel.clicked.connect(self.delete_item)
        btnUndo = QtWidgets.QPushButton("Hoàn tác")
        btnUndo.clicked.connect(self.undo)
        bot.addWidget(btnDone); bot.addWidget(btnEdit); bot.addWidget(btnDel); bot.addWidget(btnUndo)
        bot.addStretch()
        btnUp = QtWidgets.QPushButton("Lên"); btnDown = QtWidgets.QPushButton("Xuống")
        btnUp.clicked.connect(self.move_up); btnDown.clicked.connect(self.move_down)
        bot.addWidget(btnDown); bot.addWidget(btnUp)
        # Filter radios
        self.filter = QtWidgets.QButtonGroup(self)
        rbAll = QtWidgets.QRadioButton("Tất cả"); rbTodo = QtWidgets.QRadioButton("Chưa xong"); rbDone = QtWidgets.QRadioButton("Đã xong")
        rbAll.setChecked(True)
        for i,rb in enumerate([rbAll, rbTodo, rbDone]):
            self.filter.addButton(rb, i)
            rb.toggled.connect(self.refresh_all)
            bot.addWidget(rb)
        L.addLayout(bot)

        # Shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self, self.delete_item)
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, self.toggle_done)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self, self.undo)


    # ---------------- Tab 2 ----------------
    def _build_tab_day(self):
        L = QtWidgets.QVBoxLayout(self.tab_day)
        head = QtWidgets.QHBoxLayout()
        head.addWidget(QtWidgets.QLabel("Ngày"))
        self.day_sel = QtWidgets.QLineEdit(date.today().strftime(D_FMT))
        self.day_sel.setFixedWidth(110)
        head.addWidget(self.day_sel)
        btnToday = QtWidgets.QPushButton("Hôm nay")
        btnToday.clicked.connect(lambda: self._set_day_today())
        head.addWidget(btnToday)
        btnReload = QtWidgets.QPushButton("Tải lại")
        btnReload.clicked.connect(self.refresh_day)
        head.addWidget(btnReload)
        head.addWidget(QtWidgets.QLabel(f"Định dạng: {D_FMT}"))
        head.addStretch()
        L.addLayout(head)

        self.day_tbl = QtWidgets.QTableWidget(0, 4)
        self.day_tbl.setHorizontalHeaderLabels(["GIỜ","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"])
        self.day_tbl.horizontalHeader().setStretchLastSection(True)
        self.day_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        L.addWidget(self.day_tbl)

    # ---------------- Tab 3 ----------------
    def _build_tab_week(self):
        L = QtWidgets.QVBoxLayout(self.tab_week)
        head = QtWidgets.QHBoxLayout()
        head.addWidget(QtWidgets.QLabel("Tuần chứa ngày"))
        self.week_anchor = QtWidgets.QLineEdit(date.today().strftime(D_FMT))
        self.week_anchor.setFixedWidth(110)
        head.addWidget(self.week_anchor)
        btnThis = QtWidgets.QPushButton("Tuần này")
        btnThis.clicked.connect(lambda: self._set_week_this())
        head.addWidget(btnThis)
        btnReload = QtWidgets.QPushButton("Tải lại")
        btnReload.clicked.connect(self.refresh_week)
        head.addWidget(btnReload)
        head.addWidget(QtWidgets.QLabel(f"Định dạng: {D_FMT}"))
        head.addStretch()
        L.addLayout(head)

        self.week_tbl = QtWidgets.QTableWidget(0, 6)
        self.week_tbl.setHorizontalHeaderLabels(["THỨ","NGÀY","GIỜ","NỘI DUNG","ƯU TIÊN","TRẠNG THÁI"])
        self.week_tbl.horizontalHeader().setStretchLastSection(True)
        self.week_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        L.addWidget(self.week_tbl)

    # ---------------- CRUD ----------------
    def add_item(self):
        text = self.inp.text().strip()
        if not text:
            return
        due_dt, ok = QtWidgets.QInputDialog.getText(self, "Hạn chót", f"Nhập hạn chót ({DT_FMT}) hoặc để trống:", text="")
        if not ok: return
        due_dt = due_dt.strip() or None
        if due_dt and not parse_dt(due_dt):
            QtWidgets.QMessageBox.warning(self, "Sai định dạng", f"Dùng {DT_FMT}")
            return
        self.store.items.append({
            "text": text, "done": False,
            "priority": int(self.prio.currentText()),
            "due_dt": due_dt,
            "created_at": now_iso(),
            "done_at": None
        })
        self.inp.clear()
        self.refresh_all(); self.store.save()

    def _current_index(self):
        row = self.list.currentRow()
        if row < 0: return None
        mapping = self._filtered_indices()
        if 0 <= row < len(mapping):
            return mapping[row]
        return None

    def edit_item(self):
        idx = self._current_index()
        if idx is None: return
        it = self.store.items[idx]
        text, ok = QtWidgets.QInputDialog.getText(self, "Sửa", "Nội dung:", text=it["text"])
        if not ok: return
        text = text.strip()
        if not text: return
        due_dt, ok = QtWidgets.QInputDialog.getText(self, "Hạn chót", f"Nhập hạn chót ({DT_FMT}) hoặc để trống:", text=it.get("due_dt") or "")
        if not ok: return
        due_dt = due_dt.strip() or None
        if due_dt and not parse_dt(due_dt):
            QtWidgets.QMessageBox.warning(self, "Sai định dạng", f"Dùng {DT_FMT}")
            return
        it["text"] = text
        it["due_dt"] = due_dt
        self.refresh_all(); self.store.save()

    def delete_item(self):
        idx = self._current_index()
        if idx is None: return
        if QtWidgets.QMessageBox.question(self, "Xoá", "Xoá công việc đã chọn?") != QtWidgets.QMessageBox.Yes:
            return
        self._undo = ("del", idx, dict(self.store.items[idx]))
        del self.store.items[idx]
        self.refresh_all(); self.store.save()

    def undo(self):
        if not self._undo: return
        kind, idx, payload = self._undo
        if kind == "del":
            idx = min(idx, len(self.store.items))
            self.store.items.insert(idx, payload)
        self._undo = None
        self.refresh_all(); self.store.save()

    def toggle_done(self):
        idx = self._current_index()
        if idx is None: return
        it = self.store.items[idx]
        it["done"] = not it["done"]
        it["done_at"] = now_iso() if it["done"] else None
        self.refresh_all(); self.store.save()

    # ---------------- Filter + Sort ----------------
    def _is_today(self, it):
        dt = parse_dt(it.get("due_dt"))
        return bool(dt and dt.date() == date.today())

    def _is_in_week(self, it, anchor=None):
        dt = parse_dt(it.get("due_dt"))
        if not dt: return False
        a = anchor or date.today()
        return start_of_week(a) <= dt.date() <= end_of_week(a)

    def _filtered_indices(self):
        q = self.q.text().lower()
        mode = ["all","todo","done"][self.filter.checkedId()]
        rng  = self.range.currentText()
        idxs = []
        for i, it in enumerate(self.store.items):
            if mode == "todo" and it["done"]: continue
            if mode == "done" and not it["done"]: continue
            if rng == "today" and not self._is_today(it): continue
            if rng == "week" and not self._is_in_week(it): continue
            if q and q not in it["text"].lower(): continue
            idxs.append(i)
        key = self.sort.currentText()
        if key == "due_dt":
            idxs.sort(key=lambda i: (self.store.items[i]["due_dt"] is None,
                                     self.store.items[i]["due_dt"] or "9999-12-31 23:59"))
        elif key == "priority":
            idxs.sort(key=lambda i: -int(self.store.items[i].get("priority",1)))
        elif key == "created_at":
            idxs.sort(key=lambda i: self.store.items[i].get("created_at",""), reverse=True)
        return idxs

    def refresh_list(self):
        self.list.clear()
        today = date.today()
        for i in self._filtered_indices():
            it = self.store.items[i]
            badge = "[x]" if it["done"] else "[ ]"
            pr = {0:"↓",1:"=",2:"↑"}.get(int(it.get("priority",1)),"=")
            due_txt = f" | {it['due_dt']}" if it.get("due_dt") else ""
            overdue = ""
            if it.get("due_dt") and not it["done"]:
                dt = parse_dt(it["due_dt"])
                if dt and dt.date() < today:
                    overdue = "  !quá hạn"
            self.list.addItem(f"{badge} {it['text']} ({pr}){due_txt}{overdue}")
        self._update_title()

    def _update_title(self):
        total = len(self.store.items)
        done = sum(1 for x in self.store.items if x["done"])
        pct = int(done*100/total) if total else 0
        self.setWindowTitle(f"Todo List — {done}/{total} ({pct}%)")

    # ---------------- Move ----------------
    def _can_move_linear(self):
        return (self.filter.checkedId()==0 and
                not self.q.text().strip() and
                self.sort.currentText()=="default" and
                self.range.currentText()=="all")

    def move_up(self):
        if not self._can_move_linear():
            QtWidgets.QMessageBox.information(self, "Không thể di chuyển",
                "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self._current_index()
        if idx is None or idx<=0: return
        self.store.items[idx-1], self.store.items[idx] = self.store.items[idx], self.store.items[idx-1]
        self.refresh_list()
        self.list.setCurrentRow(idx-1)
        self.store.save()

    def move_down(self):
        if not self._can_move_linear():
            QtWidgets.QMessageBox.information(self, "Không thể di chuyển",
                "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self._current_index()
        if idx is None or idx>=len(self.store.items)-1: return
        self.store.items[idx+1], self.store.items[idx] = self.store.items[idx], self.store.items[idx+1]
        self.refresh_list()
        self.list.setCurrentRow(idx+1)
        self.store.save()

    # ---------------- Day view ----------------
    def _set_day_today(self):
        self.day_sel.setText(date.today().strftime(D_FMT))
        self.refresh_day()

    def refresh_day(self):
        try:
            d = datetime.strptime(self.day_sel.text().strip(), D_FMT).date()
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Lỗi ngày", f"Dùng {D_FMT}")
            return
        rows = []
        for it in self.store.items:
            dt = parse_dt(it.get("due_dt"))
            if dt and dt.date()==d:
                rows.append((dt, it))
        rows.sort(key=lambda x: x[0])
        self.day_tbl.setRowCount(0)
        for dt, it in rows:
            r = self.day_tbl.rowCount()
            self.day_tbl.insertRow(r)
            vals = [dt.strftime("%H:%M"), it["text"],
                    {0:"Thấp",1:"Thường",2:"Cao"}.get(int(it.get("priority",1)),"Thường"),
                    "Đã xong" if it.get("done") else "Chưa xong"]
            for c,v in enumerate(vals):
                self.day_tbl.setItem(r, c, QtWidgets.QTableWidgetItem(v))

    # ---------------- Week view ----------------
    def _set_week_this(self):
        self.week_anchor.setText(date.today().strftime(D_FMT))
        self.refresh_week()

    def refresh_week(self):
        try:
            anchor = datetime.strptime(self.week_anchor.text().strip(), D_FMT).date()
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Lỗi ngày", f"Dùng {D_FMT}")
            return
        monday, sunday = start_of_week(anchor), end_of_week(anchor)
        rows = []
        for it in self.store.items:
            dt = parse_dt(it.get("due_dt"))
            if dt and monday <= dt.date() <= sunday:
                rows.append((dt, it))
        rows.sort(key=lambda x: (x[0].date(), x[0].time()))
        self.week_tbl.setRowCount(0)
        for dt, it in rows:
            r = self.week_tbl.rowCount()
            self.week_tbl.insertRow(r)
            vals = [WEEKDAY_VN[dt.weekday()], dt.strftime(D_FMT), dt.strftime("%H:%M"),
                    it["text"], {0:"Thấp",1:"Thường",2:"Cao"}.get(int(it.get("priority",1)),"Thường"),
                    "Đã xong" if it.get("done") else "Chưa xong"]
            for c,v in enumerate(vals):
                self.week_tbl.setItem(r, c, QtWidgets.QTableWidgetItem(v))

    # ---------------- Orchestrate ----------------
    def refresh_all(self):
        self.refresh_list(); self.refresh_day(); self.refresh_week()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
