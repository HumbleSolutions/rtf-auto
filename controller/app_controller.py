import os
SESSION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "session.json"))
import json
import tkinter as tk
from view.login_frame import LoginFrame
from tkinter import ttk, messagebox
from view.base_frame import BaseFrame
from model.db_manager import DBManager
from view.dashboard_frame import DashboardFrame  # Ensure this is loaded here to avoid circular import

class AppController:
    def __init__(self, root):
        self.root = root
        self.frames = {}

        # Auto-login if session file exists
        if os.path.exists(SESSION_FILE):
            try:
                print("[APP INIT] Found session file:", SESSION_FILE)
                with open(SESSION_FILE) as f:
                    session = json.load(f)
                    self.user_id = session["user"]
                if LoginFrame in self.frames:
                    del self.frames[LoginFrame]
                self.show_frame(DashboardFrame)
                return
            except Exception as e:
                print("[Session Error]", e)

        self.show_frame(LoginFrame)

    def show_frame(self, frame_class, *args, **kwargs):
        """
        Instantiate and raise frame_class(self.root, self, *args, **kwargs).
        """
        if frame_class not in self.frames:
            try:
                # Pass along any positional or keyword args (e.g. mode, entity_id)
                frame = frame_class(self.root, self, *args, **kwargs)
                self.frames[frame_class] = frame
                frame.place(x=0, y=0, relwidth=1, relheight=1)

                # Only run setup_ui once per frame instance
                if not hasattr(frame, "ui_initialized"):
                    frame.setup_ui()
                    frame.ui_initialized = True

            except Exception:
                import traceback
                traceback.print_exc()
                print(f"[ERROR] Failed to load frame: {frame_class.__name__}")
                return

        # Raise the frame
        frame = self.frames[frame_class]
        frame.tkraise()

        # If the frame has a refresh_data method, call it
        if hasattr(frame, "refresh_data") and callable(frame.refresh_data):
            try:
                frame.refresh_data()
            except Exception as e:
                print("[Frame Refresh Error]", e)

    def logout(self):
        if os.path.exists(SESSION_FILE):
            print("[LOGOUT] Removing session file:", SESSION_FILE)
            os.remove(SESSION_FILE)
        self.show_frame(LoginFrame)


class LoginFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)

    def _login(self):
        uid = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()

        valid, role = DBManager().validate_user(uid, pwd)
        if valid:
            if self.remember_var.get():
                print("[LOGIN] Saved session for", uid)
                with open(SESSION_FILE, "w") as f:
                    json.dump({"user": uid, "pass": pwd}, f)
            self.controller.show_frame(DashboardFrame)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def setup_ui(self):
        username = ""
        password = ""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE) as f:
                    session = json.load(f)
                    username = session.get("user", "")
                    password = session.get("pass", "")
            except:
                pass
        self.remember_var = tk.BooleanVar(value=False)
        login_box = ttk.Frame(self)
        login_box.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(login_box, text="User ID:").pack(anchor="w")
        self.user_entry = ttk.Entry(login_box)
        self.user_entry.insert(0, username)
        self.user_entry.pack(fill="x", pady=5)

        ttk.Label(login_box, text="Password:").pack(anchor="w")
        self.pass_entry = ttk.Entry(login_box, show="*")
        self.pass_entry.insert(0, password)
        self.pass_entry.pack(fill="x", pady=5)

        ttk.Checkbutton(login_box, text="Remember me", variable=self.remember_var).pack(anchor="w", pady=5)
        login_btn = ttk.Button(login_box, text="Login", command=self._login)
        login_btn.pack(pady=10)

        self.user_entry.bind("<Return>", lambda e: self._login())
        self.pass_entry.bind("<Return>", lambda e: self._login())
