import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class WindowsMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        # New Window submenu
        new_window_menu = tk.Menu(self, tearoff=0)
        new_window_menu.add_command(label="Chart", command=self.new_chart_window)
        self.add_cascade(label="New Window", menu=new_window_menu)

        # Additional options
        self.add_command(label="Cascade", command=self.cascade_windows)
        self.add_command(label="Tile Vertical", command=self.tile_vertical)
        self.add_command(label="Tile Horizontal", command=self.tile_horizontal)
        self.add_command(label="Close All", command=self.close_all_windows)
        self.add_command(label="Arrange Icons", command=self.arrange_icons)

    def new_chart_window(self):
        chart_window = tk.Toplevel(self.master)
        chart_window.title(f"Chart {self.master.counter}")
        chart_window.geometry("400x300")
        label = tk.Label(chart_window, text=f"This is Chart Window {self.master.counter}")
        label.pack(padx=20, pady=20)
        self.master.windows.append(chart_window)
        self.master.counter += 1
        print("New Chart Window")

    def cascade_windows(self):
        x_offset = 0
        y_offset = 0
        for window in self.master.windows:
            window.geometry(f"200x200+{x_offset}+{y_offset}")
            x_offset += 30
            y_offset += 30
        print("Cascade Windows")

    def tile_vertical(self):
        total_windows = len(self.master.windows)
        if total_windows == 0:
            return

        window_width = self.master.winfo_width() // total_windows
        window_height = self.master.winfo_height()

        for index, window in enumerate(self.master.windows):
            window.geometry(f"{window_width}x{window_height}+{window_width * index}+0")
        print("Tile Windows Vertically")

    def tile_horizontal(self):
        total_windows = len(self.master.windows)
        if total_windows == 0:
            return

        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height() // total_windows

        for index, window in enumerate(self.master.windows):
            window.geometry(f"{window_width}x{window_height}+0+{window_height * index}")
        print("Tile Windows Horizontally")

    def close_all_windows(self):
        for window in self.master.windows:
            window.destroy()
        self.master.windows = []
        print("Close All Windows")

    def arrange_icons(self):
        print("Arrange Icons")