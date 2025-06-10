# view/history_frame.py

import tkinter as tk
from tkinter import ttk
from view.base_frame import BaseFrame
from model.db_manager import DBManager
from view.dashboard_frame import DashboardFrame

class ToolTip:
    def __init__(self, parent):
        self.parent = parent
        self.tipwin = None

    def show(self, text, x, y):
        self.hide()
        tw = tk.Toplevel(self.parent)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            tw, text=text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            wraplength=300
        )
        lbl.pack()
        self.tipwin = tw

    def hide(self):
        if self.tipwin:
            self.tipwin.destroy()
            self.tipwin = None

class HistoryFrame(BaseFrame):
    def __init__(self, master, controller, mode, entity_id):
        self.mode = mode
        self.entity_id = entity_id
        self.db = DBManager()
        super().__init__(master, controller)
        # BaseFrame.__init__ calls setup_ui(), but does NOT load data
        # So we load data once here:
        self.load_history()

    def setup_ui(self):
        # — Nav + Refresh bar —
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=5, padx=10)
        ttk.Button(bar, text="← Back to Dashboard",
                   command=lambda: self.controller.show_frame(DashboardFrame)
                  ).pack(side="left")
        ttk.Button(bar, text="🔄 Refresh", command=self.load_history) \
           .pack(side="right")

        # — Header —
        title = "Vehicle History" if self.mode == "vehicle" else "Customer History"
        ttk.Label(self, text=title, font=("Segoe UI", 16)) \
           .pack(pady=(0,10))

        # — Columns —
        if self.mode == "vehicle":
            cols = ("Order #","Date","KM","Issue","Status","Notes")
        else:
            cols = ("Order #","Date","Vehicle","KM","Status","Notes")

        # **Create** the Treeview BEFORE binding events**
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # — Tooltip setup & bindings (after tree exists) —
        self.tooltip = ToolTip(self)
        self._hover_after_id = None
        self._last_cell = (None, None)

        self.tree.bind("<Motion>", self._on_motion)
        self.tree.bind("<Leave>", self._on_leave)

    def load_history(self):
        # Clear old rows
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        if self.mode == "vehicle":
            rows = self.db.get_history_by_vehicle(self.entity_id)
            for oid, ts, km, issue, notes, status in rows:
                date = ts.split(" ")[0]
                self.tree.insert("", "end",
                                 values=(oid, date, km, issue, status, notes))
        else:
            rows = self.db.get_history_by_customer(self.entity_id)
            for oid, ts, make, model, year, km, issue, notes, status in rows:
                date = ts.split(" ")[0]
                vehicle = f"{make} {model} ({year})"
                self.tree.insert("", "end",
                                 values=(oid, date, vehicle, km, status, notes))

    def _on_motion(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if (row, col) == self._last_cell:
            return
        self._last_cell = (row, col)

        if self._hover_after_id:
            self.after_cancel(self._hover_after_id)
            self._hover_after_id = None
        self.tooltip.hide()

        if row and col == "#6":  # Notes column
            self._hover_after_id = self.after(
                500,
                lambda r=row, x=event.x_root, y=event.y_root: self._show_tooltip(r, x, y)
            )

    def _show_tooltip(self, row, x, y):
        text = self.tree.set(row, "#6")
        self.tooltip.show(text, x+20, y+10)
        self._hover_after_id = None

    def _on_leave(self, _):
        if self._hover_after_id:
            self.after_cancel(self._hover_after_id)
            self._hover_after_id = None
        self.tooltip.hide()
        self._last_cell = (None, None)

    # Allows AppController.show_frame to auto-refresh this frame
    def refresh_data(self):
        self.load_history()

    # No _go_back needed here since we wired the Back button inline
