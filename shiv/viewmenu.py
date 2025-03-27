import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class ViewMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.add_checkbutton(label="Toolbar", command=master.toggle_toolbar)
        self.add_checkbutton(label="Status Bar", command=master.toggle_statusbar)