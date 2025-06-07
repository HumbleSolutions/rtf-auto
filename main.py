# rtf_auto_app/main.py
import tkinter as tk
from tkinter import ttk
from controller.app_controller import AppController
from view.login_frame import LoginFrame
from helpers.logger import setup_logging
from model.db_manager import DBManager
import os

# Setup logging
setup_logging()

# Initialize DB
DBManager()._run_migrations()

class RTFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RTF Auto Shop Manager")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.controller = AppController(self)

if __name__ == "__main__":
    app = RTFApp()
    app.mainloop()
