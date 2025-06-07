# view/login_frame.py
import json
import tkinter as tk
from tkinter import ttk, messagebox
from view.base_frame import BaseFrame
from model.db_manager import DBManager

class LoginFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)

    def _login(self):
        uid = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()

        valid, role = DBManager().validate_user(uid, pwd)
        if valid:
            if self.remember_var.get():
                with open("session.json", "w") as f:
                    json.dump({"user": uid, "role": role}, f)
            self.controller.user_role = role
            from view.dashboard_frame import DashboardFrame
            self.controller.show_frame(DashboardFrame)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def setup_ui(self):
        if hasattr(self, "_ui_initialized") and self._ui_initialized:
            return
        self._ui_initialized = True
        # ... rest of your UI code ...
