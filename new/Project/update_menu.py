import time
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import messagebox, ttk

import mysql.connector
import numpy as np
import pandas as pd
from eqldata import DataClient, generate_auth_token, get_EOD, get_instrument_list
from sqlalchemy import create_engine, text
from sqlalchemy.types import Date


class CredentialDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        self.title("Select Credentials")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        # Style
        style = ttk.Style(self)
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TRadiobutton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))

        # Main frame
        main_frame = ttk.Frame(self, padding="20 20 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Credential type selection
        self.cred_type = tk.StringVar(value="default")

        ttk.Label(
            main_frame, text="Select Credential Type:", font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        ttk.Radiobutton(
            main_frame,
            text="Default Credentials",
            variable=self.cred_type,
            value="default",
            command=self.toggle_fields,
        ).pack(anchor="w", pady=5)
        ttk.Radiobutton(
            main_frame,
            text="Custom Credentials",
            variable=self.cred_type,
            value="custom",
            command=self.toggle_fields,
        ).pack(anchor="w", pady=5)

        # Credentials frame
        self.cred_frame = ttk.Frame(main_frame)
        self.cred_frame.pack(fill=tk.X, pady=(10, 20))

        # Username
        ttk.Label(self.cred_frame, text="Username:").pack(anchor="w")
        self.username_var = tk.StringVar(value="vishal.nanda@solutionsandstrategy.com")
        self.username_entry = ttk.Entry(
            self.cred_frame, textvariable=self.username_var, width=40
        )
        self.username_entry.pack(anchor="w", pady=(0, 10))

        # Password
        ttk.Label(self.cred_frame, text="Password:").pack(anchor="w")
        self.password_var = tk.StringVar(value="Hello@1234")
        self.password_entry = ttk.Entry(
            self.cred_frame, textvariable=self.password_var, show="*", width=40
        )
        self.password_entry.pack(anchor="w", pady=(0, 10))

        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(
            fill=tk.X, padx=20, pady=(0, 20), anchor="center"
        )  # Center the button frame

        # Centered and styled buttons
        ttk.Button(btn_frame, text="Submit", command=self.submit).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # Initial state
        self.toggle_fields()

        # Center the window
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def toggle_fields(self):
        if self.cred_type.get() == "default":
            self.username_entry.configure(state="disabled")
            self.password_entry.configure(state="disabled")
            # Set default values
            self.username_var.set("vishal.nanda@solutionsandstrategy.com")
            self.password_var.set("Hello@1234")
        else:
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            # Clear fields if they contain default values
            if self.username_var.get() == "vishal.nanda@solutionsandstrategy.com":
                self.username_var.set("")
            if self.password_var.get() == "Hello@1234":
                self.password_var.set("")

    def submit(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        self.callback(username, password)
        self.destroy()


class update_db(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.master = master
        self.add_command(label="Update Database", command=self.show_credential_dialog)

        # Initialize a list to hold logs
        self.logs = []

        style = ttk.Style(self)
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("TFrame", font=("Segoe UI", 12))
        style.configure("TCheckbutton", font=("Segoe UI", 12))
        style.configure("Treeview", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

    def update_credentials(self, conn, cursor, credentials):
        self.conn = conn
        self.cursor = cursor
        self.DATABASE_NAME = self.conn.database
        self.credentials = credentials

    def log_to_frame(self, message):
        self.logs.append(message)
        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)

    def create_log_frame(self):
        log_window = tk.Toplevel(self.master)
        log_window.title("Update Database Log")

        self.log_frame = ttk.Frame(log_window)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget to display logs
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Populate with current logs
        for log in self.logs:
            self.log_text.insert(tk.END, log + "\n")

        # OK Button to close the log window
        ok_button = ttk.Button(self.log_frame, text="OK", command=log_window.destroy)
        ok_button.pack(pady=10)

    def show_credential_dialog(self):
        CredentialDialog(self.master, self.start_update)

    def start_update(self, username, password):
        # Store the credentials
        self.eql_username = username
        self.eql_password = password
        # Now proceed with the database update
        self.update_database()

    def update_database(self):
        # Create a log window when updating the database
        self.create_log_frame()

        self.log_to_frame("Database update initiated...")
        HOST_ADDRESS = self.credentials["host"]
        USER_NAME = self.credentials["username"]
        PASSWORD = self.credentials["password"]

        # Create SQLAlchemy engine
        engine = create_engine(f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{HOST_ADDRESS}")

        # Create database and table if they don't exist
        with engine.connect() as connection:
            # Create database if it doesn't exist
            connection.execute(text("CREATE DATABASE IF NOT EXISTS updated_stocks"))
            connection.execute(text("USE updated_stocks"))

            # Create table if it doesn't exist
            connection.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS mstr_nse_indexes_eod (
                    Index_name VARCHAR(255),
                    Date DATE,
                    Open FLOAT,
                    High FLOAT,
                    Low FLOAT,
                    Close FLOAT,
                    Volume INT,
                    OI INT,
                    PRIMARY KEY (Index_name, Date)
                )
            """
                )
            )
            connection.commit()

        # Create a new engine with the database specified
        engine = create_engine(
            f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{HOST_ADDRESS}/updated_stocks"
        )

        try:
            # Try to get the last date, handle case when table is empty
            query = text(
                "SELECT MAX(Date) FROM mstr_nse_indexes_eod WHERE Index_name = 'NIFTY_50'"
            )
            with engine.connect() as connection:
                result = connection.execute(query)
                last_date = result.scalar()

            if last_date is None:
                # If no data exists, start from a default date
                start_update_date = date(2000, 1, 1)
                self.log_to_frame(
                    "No existing data found. Starting from "
                    + start_update_date.strftime("%Y-%m-%d")
                )
            else:
                start_update_date = last_date.date() + timedelta(days=1)
                self.log_to_frame(f"Last updated date: {last_date}")

        except Exception as e:
            # Handle any database errors
            self.log_to_frame(f"Error accessing database: {str(e)}")
            start_update_date = date(2000, 1, 1)
            self.log_to_frame("Starting from " + start_update_date.strftime("%Y-%m-%d"))

        end_update_date = date.today()

        start_update_date = start_update_date.strftime("%Y-%m-%d")
        end_update_date = end_update_date.strftime("%Y-%m-%d")

        def get_date_list(
            start_date: str, end_date: str, date_format: str = "%Y-%m-%d"
        ):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            return [
                (start_date + timedelta(days=x)).strftime(date_format)
                for x in range((end_date - start_date).days + 1)
            ]

        date_list = get_date_list(
            start_date=start_update_date, end_date=end_update_date
        )
        self.log_to_frame(f"Date list for update: {date_list}")

        try:
            auth_token = generate_auth_token(self.eql_username, self.eql_password)
            if not auth_token:
                self.log_to_frame("Failed to generate auth token. Aborting update.")
                messagebox.showerror(
                    "Error", "Authentication failed. Please check your credentials."
                )
                return

            self.log_to_frame(f"Successfully generated auth token")

            list_of_securities = get_instrument_list(auth_token)
            if not list_of_securities:
                self.log_to_frame("Failed to get instrument list. Aborting update.")
                messagebox.showerror("Error", "Could not retrieve instrument list.")
                return

            if "NSEIDX" not in list_of_securities:
                self.log_to_frame(
                    "No NSE indexes found in instrument list. Aborting update."
                )
                messagebox.showerror(
                    "Error", "No NSE indexes found in instrument list."
                )
                return

            nse_indexes = [sec for sec in list_of_securities["NSEIDX"]]

        except Exception as e:
            self.log_to_frame(f"Error during authentication/setup: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during setup: {str(e)}")
            return

        dfs = []
        for i, current_date in enumerate(date_list):
            try:
                # Check if data for current_date already exists in database
                existing_query = f"SELECT COUNT(*) FROM mstr_nse_indexes_eod WHERE Date = '{current_date}'"
                existing_data = pd.read_sql(existing_query, con=self.conn)
                if existing_data.iloc[0, 0] > 0:
                    self.log_to_frame(
                        f"Data for {current_date} already exists, skipping."
                    )
                    continue

                if i % 5 == 0:
                    time.sleep(70)

                self.log_to_frame(f"Fetching data for date: {current_date}")
                result = get_EOD(auth_token, nse_indexes, current_date)

                if result == "Error":
                    self.log_to_frame(
                        f"Couldn't get data for: {current_date} because of holidays"
                    )
                    continue
                if result == "Too Many Requests":
                    self.log_to_frame(
                        f"Couldn't get data for date: {current_date} due to server overload"
                    )
                    # Add a longer delay when hitting rate limits
                    time.sleep(120)
                    continue

                flattened_data = [item[0] for item in result if item[0]]
                if not flattened_data:
                    self.log_to_frame(f"No valid data received for {current_date}")
                    continue

                columns = [
                    "Index_name",
                    "Date",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "OI",
                ]
                df = pd.DataFrame(data=flattened_data, columns=columns)

                numeric_columns = ["Open", "High", "Low", "Close", "Volume", "OI"]
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

                df["Volume"] = df["Volume"].astype(int)
                df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")

                dfs.append(df)

            except Exception as e:
                self.log_to_frame(f"Error processing date {current_date}: {str(e)}")
                continue

        try:
            if len(dfs) > 0:
                master_df = pd.concat(dfs, ignore_index=True)
                master_df.to_sql(
                    "mstr_nse_indexes_eod",
                    con=engine,
                    index=False,
                    dtype={"Date": Date()},
                    chunksize=10000,
                    if_exists="append",
                )
                self.log_to_frame("Data successfully updated.")
                messagebox.showinfo("Success", "Database successfully updated!")
            else:
                self.log_to_frame("No new data to add for indexes.")
                messagebox.showinfo("Info", "No new data to add.")

        except Exception as e:
            self.log_to_frame(f"Error saving data to database: {str(e)}")
            messagebox.showerror("Error", f"Failed to save data to database: {str(e)}")
