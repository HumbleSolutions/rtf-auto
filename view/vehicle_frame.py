# view/vehicle_frame.py
from view.base_frame import BaseFrame
from tkinter import ttk, messagebox
from model.db_manager import DBManager
import requests

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

        self.tree = ttk.Treeview(self, columns=("ID", "Owner", "Make", "Model", "Year", "VIN", "KM"), show="headings")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=5, expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        form = ttk.Frame(self)
        form.pack(pady=5)

        self.customer_var = ttk.Combobox(form, state="readonly")
        self.make_entry = ttk.Entry(form, state="readonly")
        self.model_entry = ttk.Entry(form, state="readonly")
        self.year_entry = ttk.Entry(form, state="readonly")
        self.vin_entry = ttk.Entry(form)

        ttk.Label(form, text="Customer").grid(row=0, column=0)
        self.customer_var.grid(row=1, column=0, padx=5)
        ttk.Label(form, text="Make").grid(row=0, column=1)
        self.make_entry.grid(row=1, column=1, padx=5)
        ttk.Label(form, text="Model").grid(row=0, column=2)
        self.model_entry.grid(row=1, column=2, padx=5)
        ttk.Label(form, text="Year").grid(row=0, column=3)
        self.year_entry.grid(row=1, column=3, padx=5)
        ttk.Label(form, text="Odometer (KM)").grid(row=0, column=4)
        self.odometer_entry = ttk.Entry(form)
        self.odometer_entry.grid(row=1, column=4, padx=5)

        ttk.Label(form, text="VIN").grid(row=0, column=5)
        self.vin_entry = ttk.Entry(form)
        self.vin_entry.grid(row=1, column=5, padx=5)
        self.vin_status = ttk.Label(form, text="", foreground="green")
        self.vin_status.grid(row=1, column=7, padx=5)

        ttk.Button(form, text="Decode VIN", command=self._decode_vin).grid(row=1, column=6, padx=5)


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
        self.customer_id_map = {}
        self.customers = DBManager().get_customer_list()
        
        display_names = []
        for cust_id, full_name, *_ in self.customers:
            display_names.append(full_name)
            self.customer_id_map[full_name] = cust_id  # ✅ link name to ID

        self.customer_var['values'] = display_names





    def _get_selected_customer_id(self):
        return self.customer_id_map.get(self.customer_var.get(), None)


    def _on_select(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected, "values")
            self.selected_vehicle_id = int(data[0])  # ✅ THIS IS CRUCIAL

            self.customer_var.set(data[1])
            self.make_entry.delete(0, "end")
            self.make_entry.insert(0, data[2])
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, data[3])
            self.year_entry.delete(0, "end")
            self.year_entry.insert(0, data[4])
            self.vin_entry.delete(0, "end")
            self.vin_entry.insert(0, data[5])
            self.odometer_entry.delete(0, "end")
            self.odometer_entry.insert(0, data[6])


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
                self.vin_entry.get(),
                int(self.odometer_entry.get() or 0)

                
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_vehicle(self):
        vehicle_id = getattr(self, "selected_vehicle_id", None)
        if vehicle_id is None:
            messagebox.showerror("Error", "Select a vehicle to update first.")
            return

        customer_id = self._get_selected_customer_id()
        if customer_id is None:
            messagebox.showerror("Invalid Customer", "Please select a valid customer.")
            return

        try:
            DBManager().update_vehicle(
                vehicle_id,
                customer_id,
                self.make_entry.get(),
                self.model_entry.get(),
                self.year_entry.get(),
                self.vin_entry.get(),
                int("".join(filter(str.isdigit, self.odometer_entry.get())) or 0)
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Update Failed", str(e))


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

    def _decode_vin(self):
        vin = self.vin_entry.get().strip()
        if not vin or len(vin) < 11:
            messagebox.showerror("Invalid VIN", "Please enter a valid VIN (at least 11 characters).")
            return

        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            results = response.json()["Results"][0]

            make = results.get("Make", "").strip()
            model = results.get("Model", "").strip()
            year = results.get("ModelYear", "").strip()

            self.make_entry.config(state="normal")
            self.model_entry.config(state="normal")
            self.year_entry.config(state="normal")

            self.make_entry.delete(0, "end")
            self.model_entry.delete(0, "end")
            self.year_entry.delete(0, "end")

            self.make_entry.insert(0, make)
            self.model_entry.insert(0, model)
            self.year_entry.insert(0, year)

            self.make_entry.config(state="readonly")
            self.model_entry.config(state="readonly")
            self.year_entry.config(state="readonly")

            if not any([make, model, year]):
                self.vin_status.config(text="❌ Not Found", foreground="red")
                messagebox.showinfo("No Match", "No vehicle data was found for that VIN.")
            else:
                self.vin_status.config(text="✅ Decoded", foreground="green")
        except Exception as e:
                self.vin_status.config(text="❌ Error", foreground="red")
                messagebox.showerror("Decode Error", f"Could not decode VIN: {e}")

