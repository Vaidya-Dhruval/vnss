import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class SubWindow(tk.Toplevel):
    def __init__(self, master, number):
        super().__init__(master)
        self.title(f"Window {number}")
        self.geometry("200x200")
        label = tk.Label(self, text=f"This is Window {number}")
        label.pack(padx=20, pady=20)
        
        
class FileMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.master = master
        self.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.bind_all("<Control-n>", lambda event: self.new_file())
        self.add_command(label="Open", command=self.open_file,accelerator="Ctrl+O")
        self.bind_all("<Control-o>",lambda event: self.open_file())
        self.add_separator()
        self.add_command(label="Save", command=self.save_file,accelerator="Ctrl+S")
        self.bind_all("<Control-s>",lambda event:self.save_file())
        self.add_command(label="Save As", command=self.save_as_file)
        self.add_separator()
        self.add_command(label="Print",command=self.print_file,accelerator="Ctrl+P")
        self.bind_all("<Control-p>",lambda event:self.print_file())
        self.add_command(label="Print Review",command=self.print_review)
        self.add_command(label="Print Setup",command=self.print_setup)
        self.add_separator()
        self.add_command(label="Exit", command=master.quit)

    def new_file(self):
        window = SubWindow(self.master, self.master.counter)
        self.master.windows.append(window)
        self.master.counter += 1

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            print(f"File opened: {file_path}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            print(f"File saved: {file_path}")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            print(f"File saved as: {file_path}")
            
    def print_file(self):
        print("Print functionality invoked")
        
    def print_review(self):
        print("Print review functionality invoked")

    def print_setup(self):
        print("Print setup functionality invoked")