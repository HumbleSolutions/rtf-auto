<h1 align="center">🛠️ RTF Auto</h1>
<p align="center">
  A modern desktop management system for auto repair shops.<br>
  Built with <b>Python + Tkinter</b> • Powered by <b>SQLite</b>
</p>

---

## 🚗 Features

- 🔐 Secure role-based login system (Admin, Mechanic, Viewer)
- 👤 Customer and vehicle tracking
- 🧾 Create and manage work orders with issue notes
- 🔄 Status workflow: <code>Scheduled → In Progress → Complete</code>
- 🧰 In-Progress order tools:
  - Track parts used
  - Log mechanic hours
  - Live editable job notes
- 📅 Optional Google Calendar sync
- 📤 Planned: PDF export, signature capture, and reports

---

## 🧰 Tech Stack

| Layer     | Tech              |
|-----------|-------------------|
| UI        | Python, Tkinter   |
| Database  | SQLite            |
| Auth/API  | Google Calendar API (optional) |
| Layout    | MVC-style folder separation |

---

## 💻 Installation

### 🧾 Requirements

- Python 3.10 or higher
- Windows, macOS, or Linux

### 🔧 Setup

```bash
git clone https://github.com/YOUR_USERNAME/rtf-auto.git
cd rtf-auto
pip install -r requirements.txt
```

### ▶️ Run the App

```bash
python main.py
```

---

## 📂 Project Structure

```bash
rtf-auto/
├── main.py                          # Entry point
├── requirements.txt                 # Pip dependencies
├── README.md                        # GitHub readme
├── .gitignore                       # Ignored files

├── model/
│   └── db_manager.py                # Handles database migrations and queries

├── view/                            # All Tkinter UI frames
│   ├── base_frame.py                # Shared base class for frames
│   ├── login_frame.py               # Login screen
│   ├── dashboard_frame.py           # Navigation screen after login
│   ├── calendar_frame.py            # (Planned) calendar integration
│   ├── customer_frame.py            # Customer record manager
│   ├── vehicle_frame.py             # Vehicle tracking
│   ├── work_order_frame.py          # Work order list (Scheduled + Complete)
│   ├── in_progress_work_order_frame.py  # Editor for active orders
│   ├── in_progress_work_order_list_frame.py  # List of active work orders
│   ├── completed_work_orders_frame.py       # List of completed orders
│   └── work_order_popup.py          # Modal for creating a new work order

├── helpers/
│   ├── google_calendar_helper.py    # Google Calendar integration functions
│   └── logger.py                    # (Optional) for logging/debug output

├── exports/                         # Ignored: for CSV/PDF exports
│   └── .gitkeep                     # Keeps the folder tracked even if empty

├── assets/                          # (Optional) app icons, logos, UI images
│   └── logo.png

└── rtf_auto.db                      # Ignored: local database (auto-created)
```

---

## 🗃️ Data & Persistence

- All data is saved to a local SQLite database
- Database is auto-created with required tables on first launch
- User-generated data (work orders, vehicles, etc.) is **not** version-controlled
- Sensitive files like `token.pickle`, `session.json`, and `.db` are `.gitignore`d

---

## 📈 Version Control & Safety

This project uses Git for full version history. To revert to your last working state:

```bash
git reset --hard HEAD
```

To restore a specific backup commit:

```bash
git log
git checkout <commit_id>
```

---

## 🙋‍♂️ About This Project

RTF Auto was built to serve the real-world needs of a working mechanic shop, with a focus on speed, offline reliability, and total control over shop workflow.

---

## 📬 Contributing

Suggestions, issues, and pull requests are welcome.  
Want to customize this for your own shop? Fork away!

---

## 📜 License

MIT License — © 2025 [HumbleSolutions]
