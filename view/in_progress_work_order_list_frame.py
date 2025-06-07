from tkinter import ttk, messagebox
from view.base_frame import BaseFrame
from model.db_manager import DBManager
from view.in_progress_work_order_frame import InProgressWorkOrderFrame

class InProgressOrdersListFrame(BaseFrame):
    def __init__(self, master, controller):
        self.db = DBManager()
        super().__init__(master, controller)

    def setup_ui(self):
        ttk.Button(self, text="← Back", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="In Progress Work Orders", font=("Segoe UI", 16)).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=("ID", "Vehicle", "Issue", "Notes", "Status"),
            show="headings",
            height=12
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        self.tree.bind("<Double-1>", self._open_selected_order)

        ttk.Button(self, text="Open Selected", command=self._open_selected_order).pack(pady=(0, 10))

        self.refresh_data()

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.get_work_orders_by_status("In Progress"):
            self.tree.insert("", "end", values=row)

    def _go_back(self):
        from view.dashboard_frame import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def _open_selected_order(self, event=None):
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Select", "Select a work order to open.")
            return

        values = self.tree.item(selected, "values")
        if not values:
            messagebox.showwarning("Warning", "No values found for selection.")
            return

        work_order_id = int(values[0])
        self.controller.frames[InProgressWorkOrderFrame] = InProgressWorkOrderFrame(
            self.controller.root, self.controller, work_order_id
        )
        self.controller.frames[InProgressWorkOrderFrame].place(x=0, y=0, relwidth=1, relheight=1)
        self.controller.show_frame(InProgressWorkOrderFrame)
