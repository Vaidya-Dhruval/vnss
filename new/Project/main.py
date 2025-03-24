import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import mysql.connector
from tkcalendar import DateEntry

from buildaportfolio import BuildPortfolioMenu
from editmenu import EditMenu
from filemenu import FileMenu
from portfoliomenu import PortfolioBehaviourMenu
from predict_menu import predict
from regressionmenu import RegressionMenu
from smlmenu import smlmenu
from update_menu import update_db
from viewmenu import ViewMenu
from windowsmenu import WindowsMenu

# from databasemenu import DatabaseMenu


class StockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solutions & Strategy - Bhavya")
        self.geometry("1000x600")
        self.configure(bg="#87CEEB")

        style = ttk.Style(self)
        style.configure(
            "TLabel", font=("Segoe UI", 12)
        )  # Times New Roman font with size 14
        style.configure("TButton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("TFrame", font=("Segoe UI", 12))
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TCheckbutton", font=("Segoe UI", 12))
        style.configure("Treeview", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        self.windows = []
        self.counter = 0
        self.conn = None
        self.cursor = None

        self.create_initial_frame()
        self.main_frame = None

    def create_menu(self):
        self.menubar = tk.Menu(self)

        self.file_menu = FileMenu(self)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = EditMenu(self)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        self.view_menu = ViewMenu(self)
        self.menubar.add_cascade(label="View", menu=self.view_menu)

        self.windows_menu = WindowsMenu(self)
        self.menubar.add_cascade(label="Windows", menu=self.windows_menu)

        # self.database_menu = DatabaseMenu(self)
        # self.menubar.add_cascade(label="Database Functions", menu=self.database_menu)

        self.build_menu = BuildPortfolioMenu(self)
        self.menubar.add_cascade(label="Build A Portfolio", menu=self.build_menu)

        self.regression_menu = RegressionMenu(self)
        self.menubar.add_cascade(label="Regression", menu=self.regression_menu)

        self.portfolio_menu = PortfolioBehaviourMenu(self)
        self.menubar.add_cascade(label="Portfolio Behaviour", menu=self.portfolio_menu)

        self.sml_menu = smlmenu(self)
        self.menubar.add_cascade(label="SML", menu=self.sml_menu)

        self.predict_menu = predict(self)
        self.menubar.add_cascade(label="Predict", menu=self.predict_menu)

        self.update_menu = update_db(self)
        self.menubar.add_cascade(label="Update DB", menu=self.update_menu)

    def create_initial_frame(self):
        self.initial_frame = ttk.Frame(self)
        self.initial_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        home_frame = ttk.LabelFrame(self.initial_frame, text="Login", padding=(20, 10))
        home_frame.pack(expand=True)

        self.credential_type = tk.StringVar(value="custom")
        tk.Radiobutton(
            home_frame,
            text="Default Credentials",
            variable=self.credential_type,
            value="default",
            font=("Segoe UI", 12),
            command=self.toggle_credentials_fields,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Radiobutton(
            home_frame,
            text="Custom Credentials",
            variable=self.credential_type,
            value="custom",
            font=("Segoe UI", 12),
            command=self.toggle_credentials_fields,
        ).grid(row=0, column=1, padx=5, pady=5)
        self.credentials_frame = ttk.Frame(home_frame)
        self.credentials_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Label(self.credentials_frame, text="Host").grid(
            row=0, column=0, sticky="e", padx=(0, 5), pady=5
        )
        self.host_name = ttk.Entry(self.credentials_frame)
        self.host_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.credentials_frame, text="Username").grid(
            row=1, column=0, sticky="e", padx=(0, 5), pady=5
        )
        self.user_name = ttk.Entry(self.credentials_frame)
        self.user_name.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.credentials_frame, text="Password").grid(
            row=2, column=0, sticky="e", padx=(0, 5), pady=5
        )
        self.password = ttk.Entry(self.credentials_frame, show="*")
        self.password.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.credentials_frame, text="Database").grid(
            row=3, column=0, sticky="e", padx=(0, 5), pady=5
        )
        self.database = ttk.Entry(self.credentials_frame)
        self.database.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(home_frame, text="Login", command=self.submit_credentials).grid(
            row=2, column=0, columnspan=2, pady=10
        )
        self.toggle_credentials_fields()

    def toggle_credentials_fields(self):
        if self.credential_type.get() == "default":
            self.host_name.config(state="disabled")
            self.user_name.config(state="disabled")
            self.password.config(state="disabled")
            self.database.config(state="disabled")
        else:
            self.host_name.config(state="normal")
            self.user_name.config(state="normal")
            self.password.config(state="normal")
            self.database.config(state="normal")

    def get_credentials(self):
        if self.credential_type.get() == "default":
            return {
                "host": "localhost",
                "username": "root",
                "password": "vishva",
                "database": "updated_stocks",
            }
        else:
            return {
                "host": self.host_name.get(),
                "username": self.user_name.get(),
                "password": self.password.get(),
                "database": self.database.get(),
            }

    def submit_credentials(self):
        credentials = self.get_credentials()
        self.connect_to_database(credentials)

        if self.conn:
            self.initial_frame.destroy()
            self.main_frame = ttk.Frame(self)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            self.create_menu()
            # self.database_menu.update_credentials(self.conn, self.cursor)
            self.build_menu.update_credentials(self.conn, self.cursor)
            self.predict_menu.update_credentials(self.conn, self.cursor)
            self.update_menu.update_credentials(
                self.conn, self.cursor, self.credentials
            )
            self.config(menu=self.menubar)
            self.create_statusbar()
            self.create_toolbar()
            messagebox.showinfo(
                "Connection Successful", "Database connection established successfully."
            )
        else:
            messagebox.showerror(
                "Connection Failed", "Failed to establish database connection."
            )

    def connect_to_database(self, credentials):
        try:
            self.conn = mysql.connector.connect(
                host=credentials["host"],
                user=credentials["username"],
                password=credentials["password"],
                database=credentials["database"],
            )
            self.cursor = self.conn.cursor()
            self.credentials = credentials
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
            self.conn = None
            self.cursor = None

    def create_toolbar(self):
        self.toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        new_button = tk.Button(self.toolbar, text="New", command=self.new_document)
        new_button.pack(side=tk.LEFT)

        open_button = tk.Button(self.toolbar, text="Open", command=self.open_document)
        open_button.pack(side=tk.LEFT)

        save_button = tk.Button(self.toolbar, text="Save", command=self.save_document)
        save_button.pack(side=tk.LEFT)

        relogin_button = tk.Button(
            self.toolbar, text="Re-login", command=self.show_login_page
        )
        relogin_button.pack(side=tk.LEFT)

    def create_statusbar(self):
        self.statusbar = tk.Label(
            self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_toolbar(self):
        if self.toolbar.winfo_viewable():
            self.toolbar.pack_forget()
        else:
            self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def toggle_statusbar(self):
        if self.statusbar.winfo_viewable():
            self.statusbar.pack_forget()
        else:
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_database_functions_frame(self):
        self.clear_frame()
        DatabaseFunctionsFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def build_portfolio(self):
        self.clear_frame()
        BuildPortfolioFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def regression(self):
        self.clear_frame()
        RegressionFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def portfolio_behaviour(self):
        self.clear_frame()
        PortfolioBehaviourFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def sml(self):
        self.clear_frame()
        SMLFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def predict(self):
        self.clear_frame()
        PredictFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def update(self):
        self.clear_frame()
        UpdateFrame(self.main_frame).pack(fill=tk.BOTH, expand=True)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def new_document(self):
        self.statusbar.config(text="New document created")
        print("New document")

    def open_document(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.statusbar.config(text=f"Opened {file_path}")
            print(f"Opened {file_path}")

    def save_document(self):
        file_path = filedialog.asksaveasfilename()
        if file_path:
            self.statusbar.config(text=f"Saved to {file_path}")
            print(f"Saved to {file_path}")

    def show_login_page(self):
        # Destroy the main frame and menubar
        if self.main_frame:
            self.main_frame.destroy()
        if hasattr(self, "menubar"):
            self.config(menu="")

        # Clear the connection
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cursor = None

        # Recreate the initial frame
        self.create_initial_frame()


class DatabaseFunctionsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="DataBase Function").pack()


class BuildPortfolioFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Build Portfolio Frame").pack()


class RegressionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Regression Frame").pack()


class PortfolioBehaviourFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Portfolio Behaviour Frame").pack()


class SMLFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="SML Frame").pack()


class PredictFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Predict Frame").pack()


class UpdateFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Update Frame").pack()


if __name__ == "__main__":
    app = StockApp()
    app.mainloop()
