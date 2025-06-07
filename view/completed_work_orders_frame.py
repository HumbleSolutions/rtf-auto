# view/completed_work_orders_frame.py

from tkinter import ttk, messagebox
from view.base_frame import BaseFrame
from model.db_manager import DBManager
from view.dashboard_frame import DashboardFrame

class CompletedWorkOrdersFrame(BaseFrame):
    def __init__(self, master, controller):
        self.db = DBManager()  # must come before super().__init__
        self.selected_order_id = None
        super().__init__(master, controller)  # <- move this AFTER self.db
        if not hasattr(self, "ui_initialized"):
            self.setup_ui()
        self.ui_initialized = True
        self.refresh_data()




    def setup_ui(self):
        ttk.Button(self, text="← Back to Dashboard", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="Completed Work Orders", font=("Segoe UI", 16)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Vehicle", "Issue", "Notes", "Status", "Rate"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill="both", padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="↺ Return to In Progress", command=self._return_to_in_progress).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="❌ Delete Work Order", command=self._delete_work_order).grid(row=0, column=1, padx=10)

    def _go_back(self):
        self.controller.show_frame(DashboardFrame)

    def _on_select(self, event):
        selected = self.tree.focus()
        if selected:
            self.selected_order_id = int(self.tree.item(selected, "values")[0])

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.get_work_orders_by_status("Complete"):
            self.tree.insert("", "end", values=row)


    def _return_to_in_progress(self):
        if not self.selected_order_id:
            messagebox.showinfo("Select", "Select a work order first.")
            return
        self.db.update_work_order_status(self.selected_order_id, "In Progress")
        self.refresh_data()

    def _delete_work_order(self):
        if not self.selected_order_id:
            messagebox.showinfo("Select", "Select a work order to delete.")
            return
        confirm = messagebox.askyesno("Delete", "Are you sure you want to permanently delete this work order?")
        if confirm:
            self.db.delete_work_order(self.selected_order_id)
            self.refresh_data()
