# view/customer_frame.py
from view.base_frame import BaseFrame
from tkinter import ttk, messagebox
from model.db_manager import DBManager

class CustomerFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)

    def _go_back(self):
        from view.dashboard_frame import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def setup_ui(self):
        ttk.Button(self, text="← Back to Dashboard", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="Customer Management", font=("Segoe UI", 16)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "First", "Last", "Phone", "Email"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.pack(pady=5, expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        form = ttk.Frame(self)
        form.pack(pady=5)
        self.first = ttk.Entry(form)
        self.last = ttk.Entry(form)
        self.phone = ttk.Entry(form)
        self.email = ttk.Entry(form)
        ttk.Label(form, text="First").grid(row=0, column=0)
        self.first.grid(row=1, column=0, padx=5)
        ttk.Label(form, text="Last").grid(row=0, column=1)
        self.last.grid(row=1, column=1, padx=5)
        ttk.Label(form, text="Phone").grid(row=0, column=2)
        self.phone.grid(row=1, column=2, padx=5)
        ttk.Label(form, text="Email").grid(row=0, column=3)
        self.email.grid(row=1, column=3, padx=5)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Add", command=self._add_customer).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self._update_customer).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self._delete_customer).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Refresh", command=self.refresh_data).grid(row=0, column=3, padx=5)

    def refresh_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in DBManager().get_all_customers():
            self.tree.insert("", "end", values=row)
        self._clear_form()

    def _on_select(self, event):
        selected = self.tree.focus()
        if selected:
            data = self.tree.item(selected, "values")
            self.first.delete(0, "end")
            self.first.insert(0, data[1])
            self.last.delete(0, "end")
            self.last.insert(0, data[2])
            self.phone.delete(0, "end")
            self.phone.insert(0, data[3])
            self.email.delete(0, "end")
            self.email.insert(0, data[4])

    def _clear_form(self):
        for entry in [self.first, self.last, self.phone, self.email]:
            entry.delete(0, "end")

    def _add_customer(self):
        try:
            DBManager().add_customer(
                self.first.get(), self.last.get(), self.phone.get(), self.email.get()
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_customer(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Select Customer", "Please select a customer to update.")
            return
        cust_id = self.tree.item(selected, "values")[0]
        try:
            DBManager().update_customer(
                cust_id,
                self.first.get(),
                self.last.get(),
                self.phone.get(),
                self.email.get()
            )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_customer(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Select Customer", "Please select a customer to delete.")
            return
        cust_id = self.tree.item(selected, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure?")
        if confirm:
            DBManager().delete_customer(cust_id)
            self.refresh_data()


# Repeat similar back-button structure for VehicleFrame, WorkOrderFrame, CalendarFrame...
