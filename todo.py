#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, shutil
from datetime import datetime, date, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

DATA_FILE = "todos.json"
DT_FMT = "%Y-%m-%d %H:%M"     # 24h
D_FMT  = "%Y-%m-%d"

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def start_of_week(d: date) -> date:
    # Tuần tính từ Thứ Hai
    return d - timedelta(days=(d.weekday()))

def end_of_week(d: date) -> date:
    return start_of_week(d) + timedelta(days=6)

WEEKDAY_VN = ["Th 2","Th 3","Th 4","Th 5","Th 6","Th 7","CN"]

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Todo List")
        self.geometry("880x560")
        self.minsize(820, 520)

        self.items = []
        self._undo = None

        # ===== Notebook (3 tab) =====
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # ===== Tab 1: Danh sách =====
        self.tab_list = tk.Frame(nb)
        nb.add(self.tab_list, text="Danh sách")

        self._build_tab_list(self.tab_list)

        # ===== Tab 2: Trong ngày =====
        self.tab_day = tk.Frame(nb)
        nb.add(self.tab_day, text="Trong ngày")

        self._build_tab_day(self.tab_day)

        # ===== Tab 3: Trong tuần =====
        self.tab_week = tk.Frame(nb)
        nb.add(self.tab_week, text="Trong tuần")

        self._build_tab_week(self.tab_week)

        # Load + render
        self.load()
        self.refresh_all()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ===================== UI: Tab 1 (Danh sách) =====================
    def _build_tab_list(self, root):
        # --- Top: nhập nhanh + ưu tiên ---
        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)

        self.entry = tk.Entry(top)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.add_item())

        tk.Button(top, text="Thêm (Enter)", command=self.add_item).pack(side="left", padx=6)

        tk.Label(top, text="Ưu tiên").pack(side="left")
        self.prio_var = tk.IntVar(value=1)  # 0 Thấp, 1 Thường, 2 Cao
        tk.OptionMenu(top, self.prio_var, 0, 1, 2).pack(side="left", padx=(4,0))

        # --- Tools: tìm + sắp xếp + phạm vi ---
        tools = tk.Frame(root)
        tools.pack(fill="x", padx=8, pady=(0,8))

        tk.Label(tools, text="Tìm").pack(side="left")
        self.q = tk.StringVar()
        ent_q = tk.Entry(tools, textvariable=self.q, width=22)
        ent_q.pack(side="left", padx=(4,10))
        self.q.trace_add("write", lambda *_: self.refresh_all())

        tk.Label(tools, text="Sắp xếp").pack(side="left")
        self.sort_var = tk.StringVar(value="default")  # default|due_dt|priority|created_at
        tk.OptionMenu(tools, self.sort_var, "default", "due_dt", "priority", "created_at").pack(side="left")
        self.sort_var.trace_add("write", lambda *_: self.refresh_all())

        # Phạm vi: all | today | week
        tk.Label(tools, text="Phạm vi").pack(side="left", padx=(12,0))
        self.range_var = tk.StringVar(value="all")
        tk.OptionMenu(tools, self.range_var, "all", "today", "week").pack(side="left")
        self.range_var.trace_add("write", lambda *_: self.refresh_all())

        # --- List + scrollbar ---
        mid = tk.Frame(root)
        mid.pack(fill="both", expand=True, padx=8, pady=(0,8))

        self.listbox = tk.Listbox(mid, selectmode="browse", activestyle="dotbox")
        sb = tk.Scrollbar(mid, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # --- Bottom: actions + filter ---
        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=8)

        left = tk.Frame(bottom); left.pack(side="left")
        tk.Button(left, text="Hoàn thành (Space)", command=self.toggle_done).pack(side="left")
        tk.Button(left, text="Sửa", command=self.edit_item).pack(side="left", padx=6)
        tk.Button(left, text="Xoá (Del)", command=self.delete_item).pack(side="left")
        tk.Button(left, text="Hoàn tác", command=self.undo).pack(side="left", padx=6)

        right = tk.Frame(bottom); right.pack(side="right")
        tk.Button(right, text="Lên", command=self.move_up).pack(side="right", padx=4)
        tk.Button(right, text="Xuống", command=self.move_down).pack(side="right", padx=4)

        self.filter_var = tk.StringVar(value="all")
        for label, val in (("Tất cả", "all"), ("Chưa xong", "todo"), ("Đã xong", "done")):
            tk.Radiobutton(right, text=label, variable=self.filter_var, value=val,
                           command=self.refresh_all).pack(side="right", padx=4)

        # Shortcuts
        self.bind("<Delete>", lambda e: self.delete_item())
        self.bind("<space>", lambda e: self.toggle_done())
        self.bind("<Control-z>", lambda e: self.undo())

    # ===================== UI: Tab 2 (Trong ngày) =====================
    def _build_tab_day(self, root):
        head = tk.Frame(root); head.pack(fill="x", padx=8, pady=8)
        tk.Label(head, text="Ngày").pack(side="left")
        self.day_sel = tk.StringVar(value=date.today().strftime(D_FMT))
        tk.Entry(head, textvariable=self.day_sel, width=12).pack(side="left", padx=6)
        tk.Button(head, text="Hôm nay", command=lambda: self._set_day_today()).pack(side="left")
        tk.Button(head, text="Tải lại", command=self.refresh_day).pack(side="left", padx=6)
        tk.Label(head, text="Định dạng: YYYY-MM-DD").pack(side="left", padx=(12,0))

        # Tree: Time | Nội dung | Ưu tiên | Trạng thái
        cols = ("time","text","prio","done")
        self.day_tree = ttk.Treeview(root, columns=cols, show="headings", height=18)
        for c, w in (("time",100),("text",520),("prio",70),("done",80)):
            self.day_tree.heading(c, text=c.upper())
            self.day_tree.column(c, width=w, anchor="w")
        self.day_tree.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def _set_day_today(self):
        self.day_sel.set(date.today().strftime(D_FMT))
        self.refresh_day()

    # ===================== UI: Tab 3 (Trong tuần) =====================
    def _build_tab_week(self, root):
        head = tk.Frame(root); head.pack(fill="x", padx=8, pady=8)
        tk.Label(head, text="Tuần chứa ngày").pack(side="left")
        self.week_anchor = tk.StringVar(value=date.today().strftime(D_FMT))
        tk.Entry(head, textvariable=self.week_anchor, width=12).pack(side="left", padx=6)
        tk.Button(head, text="Tuần này", command=lambda: self._set_week_this()).pack(side="left")
        tk.Button(head, text="Tải lại", command=self.refresh_week).pack(side="left", padx=6)
        tk.Label(head, text="Định dạng: YYYY-MM-DD").pack(side="left", padx=(12,0))

        # Tree: Thứ | Ngày | Giờ | Nội dung | Ưu tiên | Trạng thái
        cols = ("dow","date","time","text","prio","done")
        self.week_tree = ttk.Treeview(root, columns=cols, show="headings", height=18)
        headers = [("dow","THỨ"),("date","NGÀY"),("time","GIỜ"),
                   ("text","NỘI DUNG"),("prio","ƯU TIÊN"),("done","TRẠNG THÁI")]
        widths  = dict(dow=60, date=100, time=80, text=460, prio=80, done=100)
        for c, h in headers:
            self.week_tree.heading(c, text=h)
            self.week_tree.column(c, width=widths[c], anchor="w")
        self.week_tree.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def _set_week_this(self):
        self.week_anchor.set(date.today().strftime(D_FMT))
        self.refresh_week()

    # ===================== Data IO =====================
    def _migrate_item(self, it: dict) -> dict:
        it = dict(it) if isinstance(it, dict) else {"text": str(it)}
        it.setdefault("text", "")
        it.setdefault("done", False)
        it.setdefault("priority", 1)          # 0 Thấp, 1 Thường, 2 Cao
        # Mới: due_dt thay cho due; vẫn chấp nhận "due" cũ và nâng cấp
        if "due_dt" not in it:
            due = it.get("due")  # có thể None hoặc "YYYY-MM-DD"
            if due:
                it["due_dt"] = f"{due} 23:59"
            else:
                it["due_dt"] = None
        it.pop("due", None)
        it.setdefault("created_at", now_iso())
        it.setdefault("done_at", None)
        return it

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.items = [self._migrate_item(x) for x in (raw if isinstance(raw, list) else [])]
            except Exception as e:
                messagebox.showwarning("Lỗi đọc dữ liệu", str(e))
                self.items = []
        else:
            self.items = []

    def save(self):
        try:
            if os.path.exists(DATA_FILE):
                shutil.copyfile(DATA_FILE, DATA_FILE + ".bak")
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Lỗi lưu", str(e))

    # ===================== Helpers =====================
    def _ask_due_dt(self, initial=None):
        s = simpledialog.askstring(
            "Hạn chót (YYYY-MM-DD HH:MM, 24h)",
            "Nhập hạn chót hoặc để trống:",
            initialvalue=initial or "",
            parent=self,
        )
        if s is None or not s.strip():
            return None
        s = s.strip()
        try:
            datetime.strptime(s, DT_FMT)
            return s
        except ValueError:
            messagebox.showerror("Sai định dạng", f"Dùng định dạng {DT_FMT}.")
            return None

    def _parse_dt(self, s):
        try:
            return datetime.strptime(s, DT_FMT) if s else None
        except Exception:
            return None

    def _is_today(self, it):
        dt = self._parse_dt(it.get("due_dt"))
        if not dt:
            return False
        return dt.date() == date.today()

    def _is_in_week(self, it, anchor_date=None):
        dt = self._parse_dt(it.get("due_dt"))
        if not dt:
            return False
        anchor = anchor_date or date.today()
        s = start_of_week(anchor); e = end_of_week(anchor)
        return s <= dt.date() <= e

    def current_index(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        visible = self.filtered_items_indices()
        idx_view = sel[0]
        if 0 <= idx_view < len(visible):
            return visible[idx_view]
        return None

    # ===================== CRUD =====================
    def add_item(self):
        text = self.entry.get().strip()
        if not text:
            return
        due_dt = self._ask_due_dt()
        self.items.append({
            "text": text,
            "done": False,
            "priority": int(self.prio_var.get()),
            "due_dt": due_dt,                 # "YYYY-MM-DD HH:MM" hoặc None
            "created_at": now_iso(),
            "done_at": None
        })
        self.entry.delete(0, "end")
        self.refresh_all()
        self.save()

    def edit_item(self):
        idx = self.current_index()
        if idx is None:
            return
        cur = self.items[idx]["text"]
        new_text = simpledialog.askstring("Sửa công việc", "Nội dung:", initialvalue=cur, parent=self)
        if new_text is None:
            return
        new_text = new_text.strip()
        if not new_text:
            return
        self.items[idx]["text"] = new_text
        new_due = self._ask_due_dt(self.items[idx].get("due_dt"))
        self.items[idx]["due_dt"] = new_due
        self.refresh_all()
        self.save()

    def delete_item(self):
        idx = self.current_index()
        if idx is None:
            return
        if not messagebox.askyesno("Xoá", "Xoá công việc đã chọn?"):
            return
        self._undo = ("del", idx, self.items[idx].copy())
        del self.items[idx]
        self.refresh_all()
        self.save()

    def undo(self):
        if not self._undo:
            return
        kind, idx, payload = self._undo
        if kind == "del":
            idx = min(idx, len(self.items))
            self.items.insert(idx, payload)
        self._undo = None
        self.refresh_all()
        self.save()

    def toggle_done(self):
        idx = self.current_index()
        if idx is None:
            return
        it = self.items[idx]
        it["done"] = not it["done"]
        it["done_at"] = now_iso() if it["done"] else None
        self.refresh_all()
        self.save()

    # ===================== Lọc + sắp xếp + render (Tab 1) =====================
    def filtered_items_indices(self):
        mode = self.filter_var.get()
        rng  = self.range_var.get()
        q = (self.q.get() or "").lower()

        indices = []
        for i, it in enumerate(self.items):
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
            indices.append(i)

        key = self.sort_var.get()
        if key == "due_dt":
            indices.sort(key=lambda i: (self.items[i]["due_dt"] is None,
                                        self.items[i]["due_dt"] or "9999-12-31 23:59"))
        elif key == "priority":
            indices.sort(key=lambda i: -int(self.items[i].get("priority", 1)))
        elif key == "created_at":
            indices.sort(key=lambda i: self.items[i].get("created_at",""), reverse=True)
        return indices

    def refresh_list(self):
        self.listbox.delete(0, "end")
        today = date.today()
        for i in self.filtered_items_indices():
            it = self.items[i]
            badge = "[x]" if it["done"] else "[ ]"
            pr = {0:"↓",1:"=",2:"↑"}.get(int(it.get("priority",1)),"=")
            due_txt = f" | {it['due_dt']}" if it.get("due_dt") else ""
            overdue = ""
            if it.get("due_dt") and not it["done"]:
                dt = self._parse_dt(it["due_dt"])
                if dt and dt.date() < today:
                    overdue = "  !quá hạn"
            label = f"{badge} {it['text']} ({pr}){due_txt}{overdue}"
            self.listbox.insert("end", label)
        self._update_stats()

    def _update_stats(self):
        total = len(self.items)
        done = sum(1 for x in self.items if x["done"])
        pct = int(done * 100 / total) if total else 0
        self.title(f"Todo List — {done}/{total} ({pct}%)")

    # ===================== Di chuyển (Tab 1) =====================
    def _can_move_linear(self):
        if self.filter_var.get() != "all":
            return False
        if (self.q.get() or "").strip():
            return False
        if self.sort_var.get() != "default":
            return False
        if self.range_var.get() != "all":
            return False
        return True

    def move_up(self):
        if not self._can_move_linear():
            messagebox.showinfo("Không thể di chuyển", "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self.current_index()
        if idx is None or idx <= 0:
            return
        self.items[idx - 1], self.items[idx] = self.items[idx], self.items[idx - 1]
        new_abs = idx - 1
        self.refresh_list()
        mapping = self.filtered_items_indices()
        if new_abs in mapping:
            view_pos = mapping.index(new_abs)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(view_pos)
            self.listbox.see(view_pos)
        self.save()

    def move_down(self):
        if not self._can_move_linear():
            messagebox.showinfo("Không thể di chuyển", "Tắt lọc/tìm/sắp xếp/phạm vi để di chuyển thứ tự.")
            return
        idx = self.current_index()
        if idx is None or idx >= len(self.items) - 1:
            return
        self.items[idx + 1], self.items[idx] = self.items[idx], self.items[idx + 1]
        new_abs = idx + 1
        self.refresh_list()
        mapping = self.filtered_items_indices()
        if new_abs in mapping:
            view_pos = mapping.index(new_abs)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(view_pos)
            self.listbox.see(view_pos)
        self.save()

    # ===================== Tab 2: render ngày =====================
    def refresh_day(self):
        # Lấy ngày
        try:
            d = datetime.strptime(self.day_sel.get().strip(), D_FMT).date()
        except Exception:
            messagebox.showerror("Lỗi ngày", f"Dùng định dạng {D_FMT}.")
            return

        # Clear
        for i in self.day_tree.get_children():
            self.day_tree.delete(i)

        # Lọc task trong ngày
        day_items = []
        for it in self.items:
            dt = self._parse_dt(it.get("due_dt"))
            if dt and dt.date() == d:
                day_items.append((dt, it))
        # Sắp xếp theo thời gian
        day_items.sort(key=lambda x: x[0])

        # Render
        for dt, it in day_items:
            time_txt = dt.strftime("%H:%M")
            pr = {0:"Thấp",1:"Thường",2:"Cao"}.get(int(it.get("priority",1)),"Thường")
            done = "Đã xong" if it.get("done") else "Chưa xong"
            self.day_tree.insert("", "end", values=(time_txt, it["text"], pr, done))

    # ===================== Tab 3: render tuần =====================
    def refresh_week(self):
        # Anchor -> tuần [Mon..Sun]
        try:
            anchor = datetime.strptime(self.week_anchor.get().strip(), D_FMT).date()
        except Exception:
            messagebox.showerror("Lỗi ngày", f"Dùng định dạng {D_FMT}.")
            return

        monday = start_of_week(anchor)
        sunday = end_of_week(anchor)

        # Clear
        for i in self.week_tree.get_children():
            self.week_tree.delete(i)

        # Lọc theo tuần
        wk = []
        for it in self.items:
            dt = self._parse_dt(it.get("due_dt"))
            if dt and monday <= dt.date() <= sunday:
                wk.append((dt, it))
        # Sắp xếp theo (day, time)
        wk.sort(key=lambda x: (x[0].date(), x[0].time()))

        # Render
        for dt, it in wk:
            dow_idx = dt.weekday()  # 0..6, Mon..Sun
            dow_txt = WEEKDAY_VN[dow_idx]
            d_txt = dt.strftime(D_FMT)
            t_txt = dt.strftime("%H:%M")
            pr = {0:"Thấp",1:"Thường",2:"Cao"}.get(int(it.get("priority",1)),"Thường")
            done = "Đã xong" if it.get("done") else "Chưa xong"
            self.week_tree.insert("", "end", values=(dow_txt, d_txt, t_txt, it["text"], pr, done))

    # ===================== Orchestrate =====================
    def refresh_all(self):
        self.refresh_list()
        self.refresh_day()
        self.refresh_week()

    # ===================== Close =====================
    def on_close(self):
        self.save()
        self.destroy()

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
