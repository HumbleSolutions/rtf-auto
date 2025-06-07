import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def open_work_order_popup(parent_frame, db, refresh_callback):
    popup = tk.Toplevel()
    popup.title("Create Work Order")
    popup.geometry("1200x700")

    for col in range(4):
        popup.grid_columnconfigure(col, weight=1)
    popup.grid_rowconfigure(1, weight=1)

    # Labels
    ttk.Label(popup, text="Vehicle").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(popup, text="Customer States").grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ttk.Label(popup, text="Notes").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    ttk.Label(popup, text="Status").grid(row=0, column=3, padx=5, pady=5, sticky="w")

    # Fields
    vehicle_dropdown = ttk.Combobox(
        popup,
        state="readonly",
        values=[f"{v[0]} - {v[1]} {v[2]} {v[3]}" for v in db.get_all_vehicles()]
    )
    vehicle_dropdown.grid(row=1, column=0, padx=5, sticky="ew")

    # Customer States checkboxes
    issue_frame = ttk.LabelFrame(popup, text="Select reported issues")
    issue_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    issue_vars = {
        "Unusual noises while driving or idling": tk.BooleanVar(),
        "Check engine light is on": tk.BooleanVar(),
        "Soft or unresponsive brakes": tk.BooleanVar(),
        "Vehicle shakes or pulls while driving": tk.BooleanVar(),
        "Hard starting, stalling, or rough idle": tk.BooleanVar(),
        "Reduced power or sluggish acceleration": tk.BooleanVar(),
        "A/C not cooling properly": tk.BooleanVar(),
        "Battery issues or dim lights": tk.BooleanVar(),
        "Fluid leaks under the vehicle": tk.BooleanVar(),
        "Clunking/popping noises over bumps or turns": tk.BooleanVar(),
        "Worn tires or rough ride": tk.BooleanVar(),
        "Overdue for oil change or service": tk.BooleanVar(),
    }

    for i, (label, var) in enumerate(issue_vars.items()):
        ttk.Checkbutton(issue_frame, text=label, variable=var).grid(row=i, column=0, sticky="w")

    notes_text = tk.Text(popup, wrap="word")
    notes_text.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

    status_var = tk.StringVar(value="Scheduled")
    ttk.Combobox(
        popup, textvariable=status_var,
        values=["Scheduled", "In Progress", "Complete"],
        state="readonly"
    ).grid(row=1, column=3, padx=5, sticky="ew")

    # Default content applied on vehicle selection
    def apply_default_template(event):
        default_notes = (
            "Perform preliminary inspection:\n"
            "- Verified concern: <describe findings>\n"
            "- Diagnostic steps taken: <describe tools/tests used>\n\n"
            "Service performed:\n"
            "- <e.g., Replaced air filter, topped off fluids>\n\n"
            "Additional findings:\n"
            "- <e.g., Front brake pads at 15%, recommend replacement soon>\n\n"
            "Post-service:\n"
            "- Test drive: <describe results>\n"
            "- Final check: <notes>\n\n"
            "Technician Notes:\n"
            "<Write detailed comments here>"
        )

        notes_text.delete("1.0", tk.END)
        notes_text.insert("1.0", default_notes)

    vehicle_dropdown.bind("<<ComboboxSelected>>", apply_default_template)

    # Submit logic
    def submit():
        try:
            vehicle_id = int(vehicle_dropdown.get().split(" - ")[0])
        except Exception:
            messagebox.showerror("Missing Field", "Please select a vehicle.")
            return

        selected_issues = [label for label, var in issue_vars.items() if var.get()]
        issue_text = "Customer states:\n" + "\n".join(f"- {issue}" for issue in selected_issues)

        notes = notes_text.get("1.0", tk.END).strip()
        status = status_var.get()
        hourly_rate = 65.0

        db.add_work_order(vehicle_id, issue_text, notes, status, hourly_rate)

        conn = db.get_connection()
        work_order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()

        popup.destroy()
        refresh_callback()

    tk.Button(popup, text="Submit", command=submit).grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky="ew")
