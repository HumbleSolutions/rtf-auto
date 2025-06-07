# view/dashboard_frame.py
from view.base_frame import BaseFrame
from tkinter import ttk, messagebox
from model.db_manager import DBManager

class DashboardFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)

    def setup_ui(self):
        ttk.Label(self, text="RTF Auto Dashboard", font=("Segoe UI", 18)).pack(pady=20)
        btns = ttk.Frame(self)
        btns.pack(pady=20)

        from view.customer_frame import CustomerFrame
        from view.vehicle_frame import VehicleFrame
        from view.work_order_frame import WorkOrderFrame
        from view.calendar_frame import CalendarFrame
        from view.completed_work_orders_frame import CompletedWorkOrdersFrame
        from view.in_progress_work_order_list_frame import InProgressOrdersListFrame

        ttk.Button(btns, text="Customers", command=lambda: self.controller.show_frame(CustomerFrame)).pack(fill="x", pady=2)
        ttk.Button(btns, text="Vehicles", command=lambda: self.controller.show_frame(VehicleFrame)).pack(fill="x", pady=2)
        ttk.Button(btns, text="Work Orders", command=lambda: self.controller.show_frame(WorkOrderFrame)).pack(fill="x", pady=2)
        ttk.Button(btns, text="✔ Completed Orders", command=lambda: self.controller.show_frame(CompletedWorkOrdersFrame)).pack(fill="x", pady=2)
        ttk.Button(btns, text="🛠 In Progress Orders", command=lambda: self.controller.show_frame(InProgressOrdersListFrame)).pack(fill="x", pady=2)
        ttk.Button(btns, text="Calendar", command=lambda: self.controller.show_frame(CalendarFrame)).pack(fill="x", pady=2)
        ttk.Button(self, text="⚙ Run Migration", command=self.run_migration).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.controller.logout).pack(pady=10)

    def run_migration(self):
        try:
            db = DBManager()
            db.rebuild_mechanic_hours()
            # Patch: add 'rate' column to work_orders if missing
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(work_orders)")
            columns = [col[1] for col in cursor.fetchall()]
            if "rate" not in columns:
                cursor.execute("ALTER TABLE work_orders ADD COLUMN rate REAL DEFAULT 65.0")
                conn.commit()
            conn.close()

        except Exception as e:
            messagebox.showerror("Migration Error", str(e))
