import datetime
import tkinter as tk
from tkinter import ttk


class smlmenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.master = master
        self.add_command(label="SML", command=self.create_widgets)

        style = ttk.Style(self)
        style.configure('TLabel', font=('Segoe UI', 12))
        style.configure('TButton', font=('Segoe UI', 12))
        style.configure('TEntry', font=('Segoe UI', 12))
        style.configure('TFrame', font=('Segoe UI', 12))
        style.configure('TCheckbutton', font=('Segoe UI', 12))
        style.configure('Treeview', font=('Segoe UI', 12))
        style.configure('Treeview.Heading', font=('Segoe UI', 12, 'bold'))

    def create_widgets(self):
        self.sml_window = tk.Toplevel(self.master)
        self.sml_window.title("Stock Prediction")
        self.sml_window.geometry("800x600") 
        # Company selection
        self.company_frame = ttk.Frame(self.sml_window)
        self.company_frame.pack(padx=5, pady=5)
        ttk.Label(self.company_frame, text="Company Name").pack(side="left")
        self.company_combo = ttk.Combobox(self.company_frame, values=["Company A", "Company B", "Company C"])
        self.company_combo.pack(side="left")

        # Exchange selection
        self.exchange_frame = ttk.Frame(self.sml_window)
        self.exchange_frame.pack(padx=5, pady=5)
        ttk.Label(self.exchange_frame, text="Choose Exchange").pack(side="left")
        self.exchange_combo = ttk.Combobox(self.exchange_frame, values=["Exchange 1", "Exchange 2", "Exchange 3"])
        self.exchange_combo.pack(side="left")

        # Date selection
        self.date_frame = ttk.Frame(self.sml_window)
        self.date_frame.pack(padx=5, pady=5)
        ttk.Label(self.date_frame, text="Start Date").pack(side="left")
        self.start_date = ttk.Entry(self.date_frame)
        self.start_date.pack(side="left")
        ttk.Label(self.date_frame, text="End Date").pack(side="left")
        self.end_date = ttk.Entry(self.date_frame)
        self.end_date.pack(side="left")

        # Index selection
        self.index_frame = ttk.Frame(self.sml_window)
        self.index_frame.pack(padx=5, pady=5)
        ttk.Label(self.index_frame, text="Select Index").pack(side="left")
        self.index_combo = ttk.Combobox(self.index_frame, values=["Auto Index", "Pharma Index", "Other Index"])
        self.index_combo.pack(side="left")

        # Buttons
        self.button_frame = ttk.Frame(self.sml_window)
        self.button_frame.pack(padx=5, pady=5)
        ttk.Button(self.button_frame, text="Calculate SML", command=self.calculate_sml).pack(side="left")
        ttk.Button(self.button_frame, text="Portfolio SML", command=self.portfolio_sml).pack(side="left")

    def calculate_sml(self):
        # Function to calculate individual stock SML
        company = self.company_combo.get()
        exchange = self.exchange_combo.get()
        start = self.start_date.get()
        end = self.end_date.get()
        index = self.index_combo.get()

        # Your SML calculation logic here
        print(f"Calculating SML for {company} on {exchange} from {start} to {end} using {index}")

    def portfolio_sml(self):
        # Function to calculate portfolio SML
        print("Calculating Portfolio SML")