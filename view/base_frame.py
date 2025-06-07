import tkinter as tk

class BaseFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # Ensure this only runs once per frame
        if not hasattr(self, 'ui_initialized') or not self.ui_initialized:
            if hasattr(self, 'setup_ui') and callable(self.setup_ui):
                self.setup_ui()
            self.ui_initialized = True
