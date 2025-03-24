import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class PortfolioBehaviourMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.add_command(label="Chart", command=self.chart)
        self.add_command(label="create a new one",command=self.initial_inputs)
        
    def chart(self):
        print("chart")
        
    def initial_inputs(self):
        print("the same initial inputs")