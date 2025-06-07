# view/vehicle_frame.py
from view.base_frame import BaseFrame
from tkinter import ttk, messagebox
from model.db_manager import DBManager

class VehicleFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)

    def _go_back(self):
        from view.dashboard_frame import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def setup_ui(self):
        ttk.Button(self, text="← Back to Dashboard", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="Vehicle Records", font=("Segoe UI", 16)).pack(pady=10)

        # --- Filter Bar ---
        filter_bar = ttk.Frame(self)
        filter_bar.pack(pady=(0, 5), fill="x", anchor="w")

        ttk.Label(filter_bar, text="Search:").pack(side="left", padx=(5, 2))
        self.search_var = ttk.Entry(filter_bar)
        self.search_var.pack(side="left", padx=2)
        ttk.Button(filter_bar, text="Apply", command=self._filter_vehicles).pack(side="left", padx=2)
        ttk.Button(filter_bar, text="Clear", command=self._clear_filter).pack(side="left", padx=2)

        self.tree = ttk.Treeview(self, columns=("ID", "Owner", "Make", "Model", "Year", "VIN"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=5, expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        form = ttk.Frame(self)
        form.pack(pady=5)

        self.customer_var = ttk.Combobox(form, state="readonly")
        self.make_entry = ttk.Entry(form)
        self.model_entry = ttk.Entry(form)
        self.year_entry = ttk.Entry(form)
        self.vin_entry = ttk.Entry(form)

        ttk.Label(form, text="Customer").grid(row=0, column=0)
        self.customer_var.grid(row=1, column=0, padx=5)
        ttk.Label(form, text="Make").grid(row=0, column=1)
        self.make_entry.grid(row=1, column=1, padx=5)
        ttk.Label(form, text="Model").grid(row=0, column=2)
        self.model_entry.grid(row=1, column=2, padx=5)
        ttk.Label(form, text="Year").grid(row=0, column=3)
        self.year_entry.grid(row=1, column=3, padx=5)
        ttk.Label(form, text="VIN").grid(row=0, column=4)
        self.vin_entry.grid(row=1, column=4, padx=5)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Add", command=self._add_vehicle).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self._update_vehicle).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self._delete_vehicle).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Refresh", command=self.refresh_data).grid(row=0, column=3, padx=5)

    def refresh_data(self):
        self._load_customers()
        self.tree.delete(*self.tree.get_children())
        for v in DBManager().get_all_vehicles():
            self.tree.insert("", "end", values=v)
        self._clear_form()

    def _load_customers(self):
        self.customers = DBManager().get_customer_list()
        self.customer_var['values'] = [f"{id} - {name}" for id, name, *_ in self.customers]

    def _get_selected_customer_id(self):
        if self.customer_var.get():
            return int(self.customer_var.get().split(" - ")[0])
        return None

    def _on_select(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected, "values")
            self.customer_var.set(data[1])
            self.make_entry.delete(0, "end")
            self.make_entry.insert(0, data[2])
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, data[3])
            self.year_entry.delete(0, "end")
            self.year_entry.insert(0, data[4])
            self.vin_entry.delete(0, "end")
            self.vin_entry.insert(0, data[5])

    def _clear_form(self):
        for field in [self.make_entry, self.model_entry, self.year_entry, self.vin_entry]:
            field.delete(0, "end")
        self.customer_var.set("")

    def _add_vehicle(self):
        try:
            DBManager().add_vehicle(
                self._get_selected_customer_id(),
                self.make_entry.get(),
                self.model_entry.get(),
                self.year_entry.get(),
                self.vin_entry.get()
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_vehicle(self):
        selected = self.tree.focus()
        if not selected:
            return
        vehicle_id = self.tree.item(selected, "values")[0]
        DBManager().update_vehicle(
            vehicle_id,
            self._get_selected_customer_id(),
            self.make_entry.get(),
            self.model_entry.get(),
            self.year_entry.get(),
            self.vin_entry.get()
        )
        self.refresh_data()

    def _delete_vehicle(self):
        selected = self.tree.focus()
        if not selected:
            return
        vehicle_id = self.tree.item(selected, "values")[0]
        DBManager().delete_vehicle(vehicle_id)
        self.refresh_data()

    def _filter_vehicles(self):
        keyword = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for v in DBManager().get_all_vehicles():
            if any(keyword in str(field).lower() for field in v):
                self.tree.insert("", "end", values=v)

    def _clear_filter(self):
        self.search_var.delete(0, "end")
        self.refresh_data()
