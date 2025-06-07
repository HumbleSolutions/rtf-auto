# view/work_order_frame.py (final patch: restored missing mechanic hour methods)
from tkinter import ttk, messagebox
from view.base_frame import BaseFrame
from model.db_manager import DBManager

class WorkOrderFrame(BaseFrame):
    def __init__(self, master, controller):
        self.db = DBManager()
        super().__init__(master, controller)

    def setup_ui(self):
        # Top bar with navigation and actions
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=5, padx=10)
        ttk.Button(top_frame, text="← Back to Dashboard", command=self._go_back).pack(side="left")
        ttk.Button(top_frame, text="Create Work Order", command=self._open_work_order_popup).pack(side="right")
        ttk.Button(top_frame, text="Convert to In Progress", command=self._convert_to_in_progress).pack(side="right", padx=10)

        ttk.Label(self, text="Work Orders", font=("Segoe UI", 16)).pack(pady=5)

        # Table display only
        self.tree = ttk.Treeview(self, columns=("ID", "Vehicle", "Issue", "Notes", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Filter bar
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)
        ttk.Label(filter_frame, text="Filter by Vehicle:").pack(side="left", padx=(0, 5))
        self.filter_entry = ttk.Entry(filter_frame, width=30)
        self.filter_entry.pack(side="left")
        ttk.Button(filter_frame, text="Apply", command=self._apply_filter).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Clear", command=self._clear_filter).pack(side="left", padx=5)

        self.refresh_tree()

    def _go_back(self):
        from view.dashboard_frame import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def _apply_filter(self):
        keyword = self.filter_entry.get().strip().lower()
        all_orders = self.db.get_all_work_orders()
        filtered = [order for order in all_orders if keyword in order[1].lower()]
        self._load_tree(filtered)

    def _clear_filter(self):
        self.filter_entry.delete(0, "end")
        self.refresh_tree()

    def refresh_tree(self):
        orders = self.db.get_all_work_orders()
        self._load_tree(orders)

    def _load_tree(self, orders):
        self.tree.delete(*self.tree.get_children())
        for order in orders:
            self.tree.insert("", "end", values=order)

    def _open_work_order_popup(self):
        from view.work_order_popup import open_work_order_popup
        open_work_order_popup(self, self.db, self.refresh_tree)

    def _convert_to_in_progress(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Select Work Order", "Please select a work order to convert.")
            return

        values = self.tree.item(selected, "values")
        work_order_id = int(values[0])
        current_status = values[4].strip()

        if current_status == "In Progress":
            messagebox.showinfo("Already In Progress", "This work order is already in progress.")
            return

        self.db.update_work_order_status(work_order_id, "In Progress")
        messagebox.showinfo("Status Updated", "Work order marked as In Progress.")
        self.refresh_tree()

    # -- Parts (already restored above) --

    # -- Mechanic Hour methods --
    def _log_time(self):
        try:
            self.db.add_mechanic_hours(
                self.work_order_id,
                self.mech_name.get(),
                float(self.mech_hours.get()),
                self.mech_date.get()
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_hour(self):
        if not hasattr(self, "selected_hour_id"):
            messagebox.showinfo("Select", "Select a log to update.")
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE mechanic_hours SET mechanic = ?, hours = ?, date = ?
                WHERE id = ?
            """, (
                self.mech_name.get(),
                float(self.mech_hours.get()),
                self.mech_date.get(),
                self.selected_hour_id
            ))
            conn.commit()
            conn.close()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_hour(self):
        if not hasattr(self, "selected_hour_id"):
            messagebox.showinfo("Select", "Select a log to delete.")
            return
        self.db.delete_mechanic_hours_entry(self.selected_hour_id)
        self.refresh_data()

    def _on_hour_select(self, event):
        selected = self.hours_tree.focus()
        if selected:
            values = self.hours_tree.item(selected, "values")
            self.selected_hour_id = int(values[0])
            self.mech_name.delete(0, "end")
            self.mech_name.insert(0, values[1])
            self.mech_hours.delete(0, "end")
            self.mech_hours.insert(0, values[2])
            self.mech_date.delete(0, "end")
            self.mech_date.insert(0, values[3])
