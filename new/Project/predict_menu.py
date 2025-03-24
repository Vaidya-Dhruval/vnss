import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
import pandas as pd
from tensorflow import keras
from keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
from keras.layers import LSTM, Dense, Dropout, Input
from keras.losses import Huber
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


class predict(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.master = master
        self.add_command(label="Predict", command=self.open_prediction_window)

        style = ttk.Style(self)
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("TFrame", font=("Segoe UI", 12))
        style.configure("TCheckbutton", font=("Segoe UI", 12))
        style.configure("Treeview", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

    def update_credentials(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.DATABASE_NAME = self.conn.database

    def open_prediction_window(self):
        self.prediction_window = tk.Toplevel(self.master)
        self.prediction_window.title("Stock Prediction")
        self.prediction_window.geometry(
            "800x600"
        )  # Increased width to accommodate multiple columns

        # Fetch unique tickers
        self.cursor.execute("SELECT DISTINCT NSETICKER FROM mstr_nse_eod")
        all_tickers = [row[0] for row in self.cursor.fetchall()]
        print("tickers fatched.....")

        # Create a frame for the checkboxes
        checkbox_frame = ttk.Frame(self.prediction_window)
        checkbox_frame.pack(pady=10, fill="both", expand=True)

        # Create a canvas and scrollbar
        canvas = tk.Canvas(checkbox_frame)
        scrollbar = ttk.Scrollbar(
            checkbox_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add checkboxes for each ticker in multiple columns
        self.ticker_vars = {}
        num_columns = 4  # You can adjust this number to change the number of columns
        tickers_per_column = -(-len(all_tickers) // num_columns)  # Ceiling division
        print("checkboxes added.......")
        for i, ticker in enumerate(all_tickers):
            column = i // tickers_per_column
            row = i % tickers_per_column
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(scrollable_frame, text=ticker, variable=var)
            cb.grid(row=row, column=column, sticky="w", padx=5, pady=2)
            self.ticker_vars[ticker] = var

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add a button to start prediction
        ttk.Button(
            self.prediction_window,
            text="Start Prediction",
            command=self.start_prediction,
        ).pack(pady=10)

        # Add a progress bar
        self.progress_bar = ttk.Progressbar(
            self.prediction_window, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

        # Add a text widget to display results
        self.result_text = tk.Text(self.prediction_window, height=10, width=70)
        self.result_text.pack(pady=10)

    def start_prediction(self):
        selected_tickers = [
            ticker for ticker, var in self.ticker_vars.items() if var.get()
        ]
        if not selected_tickers:
            tk.messagebox.showwarning(
                "No Selection", "Please select at least one stock."
            )
            return

        # Fetch data for selected tickers
        placeholders = ", ".join(["%s"] * len(selected_tickers))
        query = f"SELECT * FROM mstr_nse_eod WHERE NSETICKER IN ({placeholders})"
        self.cursor.execute(query, selected_tickers)
        rows = self.cursor.fetchall()

        # Convert to DataFrame
        columns = [desc[0] for desc in self.cursor.description]
        all_data = pd.DataFrame(rows, columns=columns)

        # Model parameters
        historical_data_length = 50
        num_features = 5
        num_lstm_nodes = 256
        num_lstm_layers = 2
        dropout_rate = 0.2
        loss_function = Huber()
        optimizer = "adam"
        batch_size = 32
        num_epochs = 50
        forecast_horizon = 1
        validation_split = 0.2

        total_steps = len(selected_tickers)
        self.progress_bar["maximum"] = total_steps

        for i, ticker in enumerate(selected_tickers):
            self.result_text.insert(tk.END, f"\nProcessing ticker: {ticker}\n")
            self.result_text.see(tk.END)
            self.result_text.update()

            ticker_data = all_data[all_data["NSETICKER"] == ticker]
            x_train, y_train, scaler = self.preprocess_data(ticker_data)

            input_shape = (x_train.shape[1], x_train.shape[2])
            model = self.create_lstm_model(
                input_shape, num_lstm_nodes, num_lstm_layers, dropout_rate
            )
            model.compile(
                optimizer=optimizer,
                loss=loss_function,
                metrics=["mae", "mse", "mean_absolute_percentage_error"],
            )

            checkpointer = ModelCheckpoint(
                filepath=f"models/{ticker}_best.keras",
                monitor="val_loss",
                verbose=0,
                save_best_only=True,
            )
            early_stopper = EarlyStopping(monitor="val_loss", patience=10, verbose=0)

            class EpochLogger(keras.callbacks.Callback):
                def __init__(self, result_text):
                    super().__init__()
                    self.result_text = result_text

                def on_epoch_end(self, epoch, logs=None):
                    self.result_text.insert(
                        tk.END, f"Epoch {epoch+1}/{num_epochs} completed\n"
                    )
                    self.result_text.see(tk.END)
                    self.result_text.update()

            epoch_logger = EpochLogger(self.result_text)

            history = model.fit(
                x_train,
                y_train,
                epochs=num_epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                callbacks=[checkpointer, early_stopper, epoch_logger],
                verbose=0,
            )
            model.load_weights(f"models/{ticker}_best.keras")

            # Predict future price
            last_data = ticker_data[["Open", "High", "Low", "Close", "Volume"]].values[
                -historical_data_length:
            ]
            predicted_price = self.predict_future_prices(
                model, last_data, historical_data_length, scaler, forecast_horizon
            )

            self.result_text.insert(
                tk.END, f"Predicted price for {ticker}: {predicted_price[0]:.2f}\n"
            )
            self.result_text.see(tk.END)
            self.result_text.update()

            # Update progress bar
            self.progress_bar["value"] = i + 1
            self.progress_bar.update()

        self.result_text.insert(
            tk.END, "\nPrediction completed for all selected stocks.\n"
        )
        self.result_text.see(tk.END)

    def preprocess_data(self, data):
        data = data[["Open", "High", "Low", "Close", "Volume"]]
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        scaled_data_df = pd.DataFrame(scaled_data, columns=data.columns)

        x, y = [], []
        for i in range(50, len(scaled_data_df) - 1):
            x.append(scaled_data_df.iloc[i - 50 : i, :].values)
            y.append(scaled_data_df.iloc[i, 3])  # Close price is at index 3
        x, y = np.array(x), np.array(y)

        return x, y, scaler

    def create_lstm_model(
        self, input_shape, num_lstm_nodes, num_lstm_layers, dropout_rate
    ):
        model = Sequential()
        model.add(Input(shape=input_shape))
        for i in range(num_lstm_layers):
            return_sequences = True if i < num_lstm_layers - 1 else False
            model.add(LSTM(units=num_lstm_nodes, return_sequences=return_sequences))
            model.add(Dropout(dropout_rate))
        model.add(Dense(units=1))
        return model

    def predict_future_prices(
        self, model, data, historical_data_length, scaler, forecast_horizon
    ):
        last_data = data[-historical_data_length:]
        scaled_last_data = scaler.transform(last_data)

        x_test = []
        x_test.append(scaled_last_data)
        x_test = np.array(x_test)

        predicted_price = model.predict(x_test)
        predicted_price = scaler.inverse_transform(
            np.hstack(
                (
                    np.zeros((predicted_price.shape[0], 3)),
                    predicted_price,
                    np.zeros((predicted_price.shape[0], 1)),
                )
            )
        )[:, 3]

        return predicted_price
