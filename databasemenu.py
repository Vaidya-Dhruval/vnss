import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import mysql.connector
from tkcalendar import DateEntry


class DatabaseMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.master = master
        self.add_command(label="Importing", command=self.show_importing_window, accelerator="Alt+I")
        self.add_command(label="Reset Panel", command=self.show_reset_panel_window, accelerator="Alt+R")
        self.bind_all("<Alt-i>", lambda event: self.show_importing_window())
        self.bind_all("<Alt-r>", lambda event: self.show_reset_panel_window())
        
        self.conn = None
        self.cursor = None
        self.min_date = None
        self.max_date = None
        
    def update_credentials(self, conn, cursor):
            self.conn=conn
            self.cursor=cursor
            self.fetch_date_range()
            
    def fetch_date_range(self):
        try:
            self.cursor.execute("SELECT MIN(Date), MAX(Date) FROM new_mstr_bse_eod")
            self.min_date, self.max_date = self.cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching date range: {e}")

    def show_importing_window(self, event=None):
        import_window = tk.Toplevel(self.master)
        import_window.title("Importing Indices")
        import_window.geometry("400x200")
        import_label = ttk.Label(import_window, text="From Date")
        import_label.grid(row=0, column=0, padx=10, pady=10)

        self.from_date_entry = DateEntry(import_window, width=12, background='darkblue', foreground='white', borderwidth=2, mindate=self.min_date, maxdate=self.max_date)
        self.from_date_entry.grid(row=0, column=1, padx=10, pady=10)

        import_button = ttk.Button(import_window, text="Import", command=self.import_data)
        import_button.grid(row=1, column=0, columnspan=2, pady=10)

    def show_reset_panel_window(self, event=None):
        reset_window = tk.Toplevel(self.master)
        reset_window.title("Reset Panel")
        reset_window.geometry("300x300")

        for i in range(5):
            reset_button = ttk.Button(reset_window, text=f"RESET{i}", command=lambda i=i: print(f"RESET{i} clicked"))
            reset_button.pack(pady=5)

        reset_all_button = ttk.Button(reset_window, text="RESET ALL", command=lambda: print("RESET ALL clicked"))
        reset_all_button.pack(pady=10)
        
    def import_data(self):
        selected_date = self.from_date_entry.get_date()
        formatted_date = selected_date.strftime('%Y-%m-%d')
        query = "SELECT * FROM new_mstr_bse_eod WHERE Date >= %s ORDER BY Date"
        self.cursor.execute(query, (formatted_date,))
        result = self.cursor.fetchall()

        if not result:
            messagebox.showinfo("No Data", "No data found for the selected date.")
            return
        
        display_window = tk.Toplevel(self.master)
        display_window.title(f"Data for {formatted_date}")
        display_window.geometry("800x600")

        style = ttk.Style()
        style.configure("mystyle.Treeview",
                        font=('Calibri', 12),
                        rowheight=25,
                        bordercolor='black',
                        borderwidth=5,
                        relief='solid')
        style.configure("mystyle.Treeview.Heading",
                        font=('Calibri', 14, 'bold'),
                        background="gray",
                        foreground="white")  # Change heading background and text color
        style.map("mystyle.Treeview.Heading",background=[('active', 'gray')])  # Change active heading background color
        
        tree = ttk.Treeview(display_window, columns=("NSETICKER", "Date", "Open", "High", "Low", "Close", "Volume", "OI"), show="headings",style='mystle.Treeview.Heading')
        tree.heading("NSETICKER", text="NSETICKER")
        tree.heading("Date", text="Date")
        tree.heading("Open", text="Open")
        tree.heading("High", text="High")
        tree.heading("Low", text="Low")
        tree.heading("Close", text="Close")
        tree.heading("Volume", text="Volume")
        tree.heading("OI", text="OI")
        tree.pack(fill=tk.BOTH, expand=True)

        tree.tag_configure('oddrow', background='lightblue')
        tree.tag_configure('evenrow', background='gray')
        
        for i,row in enumerate(result):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", tk.END, values=row, tags=(tag,))
