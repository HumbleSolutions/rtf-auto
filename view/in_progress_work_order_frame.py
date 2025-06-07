# view/in_progress_work_order_frame.py (fully restored functionality)
from tkinter import ttk, messagebox
import tkinter as tk
from tkcalendar import DateEntry
from view.base_frame import BaseFrame
from model.db_manager import DBManager

class InProgressWorkOrderFrame(BaseFrame):
    def __init__(self, master, controller, work_order_id):
        self.db = DBManager()
        self.work_order_id = work_order_id
        super().__init__(master, controller)

    def setup_ui(self):
        ttk.Button(self, text="← Back", command=self._go_back).pack(pady=5, anchor="w")
        ttk.Label(self, text="In Progress Work Order", font=("Segoe UI", 16)).pack(pady=10)

        notes_frame = ttk.Frame(self)
        notes_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.notes_text = tk.Text(notes_frame, height=6, wrap="word")
        self.notes_text.pack(fill="x", expand=True)
        ttk.Button(self, text="Update Notes", command=self._update_notes).pack(pady=(0, 10))

        wrapper = ttk.Frame(self)
        wrapper.pack(fill="both", expand=True, padx=10)

        parts_frame = ttk.LabelFrame(wrapper, text="Parts Used")
        parts_frame.pack(side="left", expand=True, fill="both", padx=10, pady=5)

        part_form = ttk.Frame(parts_frame)
        part_form.pack(pady=(5, 0))

        self.part_name = ttk.Entry(part_form)
        self.part_qty = ttk.Entry(part_form)
        self.part_price = ttk.Entry(part_form)

        ttk.Label(part_form, text="Part").grid(row=0, column=0)
        self.part_name.grid(row=1, column=0, padx=5)
        ttk.Label(part_form, text="Qty").grid(row=0, column=1)
        self.part_qty.grid(row=1, column=1, padx=5)
        ttk.Label(part_form, text="Unit Price").grid(row=0, column=2)
        self.part_price.grid(row=1, column=2, padx=5)
        ttk.Button(part_form, text="Add Part", command=self._add_part).grid(row=1, column=3, padx=5)
        ttk.Button(part_form, text="Update Part", command=self._update_part).grid(row=1, column=4, padx=5)
        ttk.Button(part_form, text="Delete Part", command=self._delete_part).grid(row=1, column=5, padx=5)

        self.parts_tree = ttk.Treeview(parts_frame, columns=("ID", "Part", "Qty", "Unit $", "Total $"), show="headings", height=10)
        for col in self.parts_tree["columns"]:
            self.parts_tree.heading(col, text=col)
            self.parts_tree.column(col, width=110)
        self.parts_tree.pack(pady=(5, 5), fill="both", expand=True)
        self.parts_tree.bind("<<TreeviewSelect>>", self._on_part_select)

        hours_frame = ttk.LabelFrame(wrapper, text="Mechanic Hours")
        hours_frame.pack(side="left", expand=True, fill="both", padx=10, pady=5)

        hours_form = ttk.Frame(hours_frame)
        hours_form.pack(pady=(5, 0))

        self.mech_name = ttk.Entry(hours_form)
        self.mech_hours = ttk.Entry(hours_form)
        self.mech_date = DateEntry(hours_form, width=12)

        ttk.Label(hours_form, text="Mechanic").grid(row=0, column=0)
        self.mech_name.grid(row=1, column=0, padx=5)
        ttk.Label(hours_form, text="Hours").grid(row=0, column=1)
        self.mech_hours.grid(row=1, column=1, padx=5)
        ttk.Label(hours_form, text="Date").grid(row=0, column=2)
        self.mech_date.grid(row=1, column=2, padx=5)
        ttk.Button(hours_form, text="Log Time", command=self._log_time).grid(row=1, column=3, padx=5)
        ttk.Button(hours_form, text="Update Entry", command=self._update_hour).grid(row=1, column=4, padx=5)
        ttk.Button(hours_form, text="Delete Entry", command=self._delete_hour).grid(row=1, column=5, padx=5)

        self.hours_tree = ttk.Treeview(hours_frame, columns=("ID", "Mechanic", "Hours", "Date"), show="headings", height=8)
        for col in self.hours_tree["columns"]:
            self.hours_tree.heading(col, text=col)
            self.hours_tree.column(col, width=110)
        self.hours_tree.pack(pady=(5, 5), fill="both", expand=True)
        self.hours_tree.bind("<<TreeviewSelect>>", self._on_hour_select)

        self.total_hours_var = tk.StringVar(value="Total Hours: 0.0")
        ttk.Label(hours_frame, textvariable=self.total_hours_var, font=("Segoe UI", 10, "italic")).pack(pady=(0, 5))
        self.subtotal_var = tk.StringVar(value="Work Order Subtotal: $0.00")
        ttk.Label(self, textvariable=self.subtotal_var, font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))

        self.refresh_data()

    def refresh_data(self):
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", self.db.get_notes_for_work_order(self.work_order_id))

        # Parts
        self.parts_tree.delete(*self.parts_tree.get_children())
        parts = self.db.get_parts_for_work_order(self.work_order_id)
        for row in parts:
            total = float(row[2]) * float(row[3])
            self.parts_tree.insert("", "end", values=(row[0], row[1], row[2], f"${row[3]:.2f}", f"${total:.2f}"))
        part_total = sum(float(row[4]) for row in parts)

        # Hours
        self.hours_tree.delete(*self.hours_tree.get_children())
        hours = self.db.get_mechanic_hours(self.work_order_id)
        total_hours = 0.0
        for row in hours:
            self.hours_tree.insert("", "end", values=row)
            total_hours += float(row[2])
        self.total_hours_var.set(f"Total Hours: {total_hours:.2f}")

        # Subtotal
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rate FROM work_orders WHERE id = ?", (self.work_order_id,))
        row = cursor.fetchone()
        conn.close()
        rate = float(row[0]) if row else 0.0
        labor_total = total_hours * rate
        subtotal = part_total + labor_total
        self.subtotal_var.set(f"Work Order Subtotal: ${subtotal:.2f}")

    def _go_back(self):
        from view.in_progress_work_order_list_frame import InProgressOrdersListFrame
        self.controller.show_frame(InProgressOrdersListFrame)

    def _update_notes(self):
        try:
            notes = self.notes_text.get("1.0", "end").strip()
            self.db.update_work_order_notes(self.work_order_id, notes)
            messagebox.showinfo("Success", "Notes updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add_part(self):
        try:
            qty = int(self.part_qty.get())
            unit_price = float(self.part_price.get())
            total = qty * unit_price
            self.db.add_part_to_work_order(self.work_order_id, self.part_name.get(), qty, unit_price, total)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_part(self):
        if not hasattr(self, "selected_part_id"):
            messagebox.showinfo("Select", "Select a part to update.")
            return
        try:
            qty = int(self.part_qty.get())
            unit = float(self.part_price.get())
            cost = qty * unit
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE work_order_parts SET part_name = ?, quantity = ?, unit_price = ?, cost = ?
                WHERE id = ?
            """, (self.part_name.get(), qty, unit, cost, self.selected_part_id))
            conn.commit()
            conn.close()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_part(self):
        if not hasattr(self, "selected_part_id"):
            messagebox.showinfo("Select", "Select a part to delete.")
            return
        try:
            self.db.delete_work_order_part(self.selected_part_id)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_part_select(self, event):
        selected = self.parts_tree.focus()
        if selected:
            values = self.parts_tree.item(selected, "values")
            self.selected_part_id = int(values[0])
            self.part_name.delete(0, "end")
            self.part_name.insert(0, values[1])
            self.part_qty.delete(0, "end")
            self.part_qty.insert(0, values[2])
            self.part_price.delete(0, "end")
            self.part_price.insert(0, values[3].replace("$", ""))

    def _log_time(self):
        try:
            self.db.add_mechanic_hours(
                self.work_order_id,
                self.mech_name.get(),
                float(self.mech_hours.get()),
                self.mech_date.get_date().isoformat()
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
                self.mech_date.get_date().isoformat(),
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

    def calculate_subtotal(self):
        parts = self.db.get_parts_for_work_order(self.work_order_id)
        part_total = sum(float(row[4]) for row in parts)

        hours = self.db.get_mechanic_hours(self.work_order_id)
        total_hours = sum(float(row[2]) for row in hours)

        # Get hourly rate from work_order
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rate FROM work_orders WHERE id = ?", (self.work_order_id,))
        row = cursor.fetchone()
        conn.close()
        rate = float(row[0]) if row else 0.0

        labor_total = total_hours * rate
        subtotal = part_total + labor_total
        self.subtotal_var.set(f"Work Order Subtotal: ${subtotal:.2f}")
