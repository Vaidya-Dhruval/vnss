
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class EditMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.add_command(label="Undo", command=self.undo,accelerator="Ctrl+z")
        self.bind_all("<Control-z>",lambda event:self.undo())
        self.add_command(label="Redo", command=self.redo,accelerator="Ctrl+y")
        self.bind_all("<Control-y>",lambda event:self.redo())
        self.add_separator()
        self.add_command(label="cut",command=self.cut,accelerator="Ctrl+x")
        self.bind_all("<Control-x>",lambda event:self.cut())
        self.add_command(label="copy",command=self.copy,accelerator="Ctrl+c")
        self.bind_all("<Control-c>",lambda event:self.copy())
        self.add_command(label="paste",command=self.paste,accelerator="Ctrl+v")
        self.bind_all("<Control-v>",lambda event:self.paste())
        
        self.add_separator()
        self.add_command(label="select All",command=self.select_all,accelerator="Ctrl+a")
        self.bind_all("<Control-a>",lambda event:self.select_all())

    def undo(self):
        print("Undo")

    def redo(self):
        print("Redo")
        
    def cut(self):
        print("cut")
    
    def copy(self):
        print("copy")

    def paste(self):
        print("paste")
        
    def select_all(self):
        print("select all")