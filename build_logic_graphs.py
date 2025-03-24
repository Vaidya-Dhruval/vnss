import copy
import tkinter as tk
from datetime import date as date_type
from datetime import datetime, time, timedelta
from tkinter import filedialog, messagebox, ttk

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import date2num, num2date
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from tkcalendar import DateEntry

pd.set_option('display.float_format','{:.10f}'.format)

index_to_table_df = pd.read_csv(r'C:\Users\vishv\python\internship\source_code\index_to_table_mapping_nse.csv')
temp_dict = index_to_table_df.to_dict()
abc = dict()
for i in range(len(temp_dict['index'])):
    # bcd = zip(temp_dict["index"][i],temp_dict["table_name"][i])
    abc[temp_dict["index"][i]] = temp_dict["table_name"][i]

INDEX_TO_REGRESS_WITH_BSE = "SENSEX"
INDEX_TO_REGRESS_WITH_NSE = "Nifty 50"

INDEX_TO_TABLES_MAPPING_BSE = {
    "bse100":"mstr_bse100_index",
    "bse200" : "mstr_bse200_index",
    "bse500" : "mstr_bse500_index",
    "auto"  : "mstr_bse_auto",
    "bankex" : "mstr_bse_bankex",
    "cap goods": "mstr_bse_cap_goods",
    "consumer durables" : "mstr_bse_cons_dur",
    "Fmcg" : "mstr_bse_fmcg",
    "greenex" : "mstr_bse_greenex",
    "Health Care" : "mstr_bse_health_care",
    "ipo index" : "mstr_bse_ipo_index",
    "IT" : "mstr_bse_it",
    "metal" : "mstr_bse_metal", 
    "MidCap" : "mstr_bse_midcap",
    "OilGas" : "mstr_bse_oilgas",
    "Power" : "mstr_bse_power", 
    "PSU" : "mstr_bse_psu",
    "Realty" : "mstr_bse_realty",
    "Sectoral"  : "mstr_bse_sectoral", 
    "Sensex"    : "mstr_bse_sensex",
    "Small Cap" : "mstr_bse_smallcap",
    "Tasis Shariah": "mstr_bse_tasis_shariah",
    "teck"  : "mstr_bse_teck"
}
INDEX_TO_TABLES_MAPPING_NSE = abc
STOCK_INDEXES = [] #append from BSE indices checkbutton
GROUP = [] #provide option & append here checkbutton
RATE_RISK_FREE_RETURN_BSE = 0
RATE_RISK_FREE_RETURN_NSE = 7
RATE_RISK_FREE_RETURN_NSE = RATE_RISK_FREE_RETURN_NSE/365
# STOCK_EXCHANGE=""
current_annotation = None

class BuildPortfolioMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.add_command(label="Initial Inputs", command=self.initial_inputs)
        self.add_command(label="Enter Risk Free Rate of Return", command=self.risk_free_return)
        self.add_command(label="Data Grid View", command=self.grid_view)
        self.START_DATE=None
        self.END_DATE=None
        self.conn=None
        self.cursor=None
        
    def update_credentials(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor
        self.DATABASE_NAME=self.conn.database
        
    def initial_inputs(self):
        # Use self as the parent window
        exchanges_frame = ttk.LabelFrame(self, text="Exchanges")
        exchanges_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        group_frame = ttk.LabelFrame(self, text="Group")
        group_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        bse_indices_frame = ttk.LabelFrame(self, text="BSE Indices")
        bse_indices_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        nse_indices_frame = ttk.LabelFrame(self, text="NSE Indices")
        nse_indices_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        self.canvas = tk.Canvas(nse_indices_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = ttk.Scrollbar(nse_indices_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame inside the canvas to hold the checkboxes
        self.nse_indices_inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.nse_indices_inner_frame, anchor="nw")

        commodities_frame = ttk.LabelFrame(self, text="Commodities")
        commodities_frame.grid(row=0, column=4, padx=10, pady=10, sticky="nsew")

        forex_frame = ttk.LabelFrame(self, text="Forex")
        forex_frame.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

        time_period_frame = ttk.LabelFrame(self, text="Select Time Period")
        time_period_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.exchange_var = tk.StringVar()
        self.exchange_var.trace("w", self.update_indices_state)
        ttk.Radiobutton(exchanges_frame, text="Bombay Stock Exchange", variable=self.exchange_var, value="BSE").pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(exchanges_frame, text="National Stock Exchange", variable=self.exchange_var, value="NSE").pack(anchor='w', padx=5, pady=2)

        # Add widgets to the group
        self.group_vars = [tk.BooleanVar() for _ in range(2)]
        group_option = ['A', 'B']
        self.group_widgets = []
        for i, text in enumerate(group_option):
            var = self.group_vars[i]
            widget = ttk.Checkbutton(group_frame, text=text, variable=var)
            widget.pack(anchor='w', padx=5, pady=2)
            self.group_widgets.append(widget)

        # Add widgets to the BSE indices frame
        self.bse_indices_vars = [tk.BooleanVar() for _ in range(23)]
        bse_indices = ['bse100', 'bse200', 'bse500', 'auto', 'bankex', 'cap goods', 'consumer durables', 'Fmcg', 'greenex', 'Health Care', 'ipo index', 'IT', 'metal', 'MidCap', 'OilGas', 'Power', 'PSU', 'Realty', 'Sectoral', 'Sensex', 'Small Cap', 'Tasis Shariah', 'teck']

        self.bse_indices_widgets = []
        for i, text in enumerate(bse_indices):
            var = self.bse_indices_vars[i]
            widget = ttk.Checkbutton(bse_indices_frame, text=text, variable=var)
            widget.pack(anchor='w', padx=5, pady=2)
            self.bse_indices_widgets.append(widget)
            if text == "BSE ALL":
                var.trace("w", lambda *args, v=var: self.handle_all_indices(v, self.bse_indices_vars, self.bse_indices_widgets))

        # Add widgets to the NSE indices frame
        self.nse_indices_widgets = []
        self.nse_indices_vars = [tk.BooleanVar() for _ in range(77)]
        nse_indices = [
            "nifty_50",
            "nifty_next_50",
            "nifty_100",
            "nifty_200",
            "nifty_500",
            "nifty_midcap_50",
            "nifty_midcap_100",
            "nifty_smallcap_100",
            "india_vix",
            "nifty_midcap_150",
            "nifty_smallcap_50",
            "nifty_smallcap_250",
            "nifty_midsmallcap_400",
            "nifty500_multicap_50:25:25",
            "nifty_largemidcap_250",
            "nifty_midcap_select",
            "nifty_total_market",
            "nifty_microcap_250",
            "nifty_bank",
            "nifty_auto",
            "nifty_financial_services",
            "nifty_financial_services_25/50",
            "nifty_fmcg",
            "nifty_it",
            "nifty_media",
            "nifty_metal",
            "nifty_pharma",
            "nifty_psu_bank",
            "nifty_private_bank",
            "nifty_realty",
            "nifty_healthcare_index",
            "nifty_consumer_durables",
            "nifty_oil_&_gas",
            "nifty_midsmall_healthcare",
            "nifty_dividend_opportunities_50",
            "nifty_growth_sectors_15",
            "nifty100_quality_30",
            "nifty50_value_20",
            "nifty50_tr_2x_leverage",
            "nifty50_pr_2x_leverage",
            "nifty50_tr_1x_inverse",
            "nifty50_pr_1x_inverse",
            "nifty50_dividend_points",
            "nifty_alpha_50",
            "nifty50_equal_weight",
            "nifty100_equal_weight",
            "nifty100_low_volatility_30",
            "nifty200_quality_30",
            "nifty_alpha_low_volatility_30",
            "nifty200_momentum_30",
            "nifty_midcap150_quality_50",
            "nifty200_alpha_30",
            "nifty_midcap150_momentum_50",
            "nifty_commodities",
            "nifty_india_consumption",
            "nifty_cpse",
            "nifty_energy",
            "nifty_infrastructure",
            "nifty100_liquid_15",
            "nifty_midcap_liquid_15",
            "nifty_mnc",
            "nifty_pse",
            "nifty_services_sector",
            "nifty100_esg_sector_leaders",
            "nifty_india_digital",
            "nifty100_esg",
            "nifty_india_manufacturing",
            "nifty_india_corporate_group_index___tata_group_25%_cap",
            "nifty500_multicap_india_manufacturing_50:30:20",
            "nifty500_multicap_infrastructure_50:30:20",
            "nifty_8_13_yr_g_sec",
            "nifty_10_yr_benchmark_g_sec",
            "nifty_10_yr_benchmark_g_sec_(clean_price)",
            "nifty_4_8_yr_g_sec_index",
            "nifty_11_15_yr_g_sec_index",
            "nifty_15_yr_and_above_g_sec_index",
            "nifty_composite_g_sec_index"
        ]

        for i, text in enumerate(nse_indices):
            var = self.nse_indices_vars[i]
            widget = ttk.Checkbutton(self.nse_indices_inner_frame, text=text, variable=var)
            widget.pack(anchor='w', padx=5, pady=2)
            self.nse_indices_widgets.append(widget)
            if text == "NSE ALL":
                var.trace("w", lambda *args, v=var: self.handle_all_indices(v, self.nse_indices_vars, self.nse_indices_widgets))

        # Add widgets to the commodities frame
        self.gold_var = tk.BooleanVar()
        ttk.Checkbutton(commodities_frame, text="Gold", variable=self.gold_var).pack(anchor='w', padx=5, pady=2)

        # Add widgets to the forex frame
        self.forex_vars = [tk.BooleanVar() for _ in range(4)]
        forex = ["US Dollar", "Great Britain Pound", "Euro", "Japanese Yen"]
        for i, text in enumerate(forex):
            ttk.Checkbutton(forex_frame, text=text, variable=self.forex_vars[i]).pack(anchor='w', padx=5, pady=2)

        # Add widgets to the time period frame
        ttk.Label(time_period_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.start_date_entry = DateEntry(time_period_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(time_period_frame, text="End Date:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.end_date_entry = DateEntry(time_period_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(time_period_frame, text="Interval:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.interval_entry = ttk.Entry(time_period_frame)
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)

        self.next_button = ttk.Button(time_period_frame, text="Next >", command=self.execute)
        self.next_button.grid(row=3, column=1, padx=5, pady=5)

        
    def execute(self):
        self.calculations()
        self.risk_free_return()



    def calculations(self):
        STOCK_INDEXES = [self.nse_indices_widgets[i].cget("text") for i, var in enumerate(self.nse_indices_vars) if var.get()]
        self.START_DATE = self.start_date_entry.get_date()
        self.END_DATE = self.end_date_entry.get_date()
        try:
            INTERVAL = int(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for the interval.")
            return
        
        self.START_DATE = pd.to_datetime(self.START_DATE)
        day = self.START_DATE.day_name()
        if(day == "Sunday"):
            self.START_DATE = self.START_DATE - pd.Timedelta(days=2)
        else:
            self.START_DATE = pd.to_datetime(self.START_DATE) - pd.Timedelta(days=1)
        self.START_DATE = self.START_DATE.date()
        
        stock_df_list = []
        for stock_index in STOCK_INDEXES:
            stock_index_name = INDEX_TO_TABLES_MAPPING_NSE[stock_index]
            query = f"SELECT m.NSETICKER,il.Index_Code,il.Index_name,e.Date,e.Close FROM  mstr_{STOCK_EXCHANGE}_stocks_list m INNER JOIN {stock_index_name} i on m.NSETICKER = i.NSETICKER INNER JOIN mstr_{STOCK_EXCHANGE}_index_list il ON i.Index_code = il.Index_code INNER JOIN mstr_{STOCK_EXCHANGE}_eod e ON m.NSETICKER = e.NSETICKER WHERE e.Date BETWEEN '{self.START_DATE}' AND '{self.END_DATE}'"
            temp_df = pd.read_sql_query(query,self.conn)
            stock_df_list.append(temp_df)

        final_df = pd.concat(stock_df_list,ignore_index=True)
        final_df["Date"] = pd.to_datetime(final_df["Date"])
        
        temp = pd.read_sql_query(f"select * from {self.DATABASE_NAME}.mstr_{STOCK_EXCHANGE}_indexes_eod WHERE Index_name = '{INDEX_TO_REGRESS_WITH_NSE}' AND Date BETWEEN '{self.START_DATE}' AND '{self.END_DATE}' ",self.conn)
        temp = temp[["Index_name","Date","Close"]]
        #renaming the column close to close market as to not confuse it with close of stocks 
        temp.rename(columns={
            "Close":"close_market"
        },inplace=True)
        temp["Date"] = pd.to_datetime(temp["Date"])
        
        df313 = pd.merge(final_df,temp, how="inner",left_on="Date",right_on="Date" )
        df313 = pd.merge(final_df,temp, how="inner",left_on="Date",right_on="Date")
        df313 = df313[["NSETICKER","Index_name_x","Date","Close","Index_name_y","close_market"]]
        df313.rename(columns={
            "Index_name_x":"index_of_stock",
            "Index_name_y": "index_to_regress_with",
            "Close": "Close_stock",
            "close_market": "Close_market_index"
            
        },inplace=True)
        
        self.df_512 = {name:group for name,group in df313.groupby("NSETICKER")}


        for key in self.df_512:
            self.df_512[key] = self.df_512[key].iloc[::INTERVAL+1] # logic to implement interval 
            self.df_512[key] = self.df_512[key].sort_values(by="Date")
            self.df_512[key]["Previous_Close_stock"] = self.df_512[key]["Close_stock"].shift(1)
            self.df_512[key]["Previous_Close_market"] = self.df_512[key]["Close_market_index"].shift(1)
            self.df_512[key].dropna(inplace=True)

            self.df_512[key]["Return_Stock"] = ( self.df_512[key]["Close_stock"] - self.df_512[key]["Previous_Close_stock"] ) / self.df_512[key]["Previous_Close_stock"]
            self.df_512[key]["Return_market"] = ( self.df_512[key]["Close_market_index"] - self.df_512[key]["Previous_Close_market"] ) / self.df_512[key]["Previous_Close_market"]


            self.df_512[key]["returns_percentage"] = self.df_512[key]["Return_Stock"] * 100
            self.df_512[key]["returns_market_percentage"] = self.df_512[key]["Return_market"] * 100
            
        results = []
        for stock in self.df_512:

            stock_return = self.df_512[stock]["returns_percentage"].to_numpy().reshape(-1,1)
            market_return = self.df_512[stock]["returns_market_percentage"].to_numpy().reshape(-1,1)

            model = LinearRegression()
            model.fit(market_return,stock_return)
            BETA = model.coef_[0][0]
            ALPHA = model.intercept_[0]
            mean_returns_stock = self.df_512[stock]["Return_Stock"].mean()
            std_deviation_stock = self.df_512[stock]["Return_Stock"].std()
            variance_stock = std_deviation_stock ** 2
            std_deviation_market = self.df_512[stock]["Return_market"].std()
            variance_market = std_deviation_market ** 2
            mean_returns_percentage_stock = self.df_512[stock]["returns_percentage"].mean()
            
            

            co_relation = self.df_512[stock]["Close_stock"].corr(self.df_512[stock]["Close_market_index"])
            unsystematic_risk = variance_stock - ((BETA)**2  * variance_market )
            length_of_df = len(self.df_512[stock])

            results.append(
                
                { "NSETICKER": self.df_512[stock]["NSETICKER"].iloc[0],
                "no_of_rows": len(self.df_512[stock]),
                "mean_returns_stock": mean_returns_stock,
                "returns_percentage": mean_returns_percentage_stock,
                "annualized_returns_percentage (mean_daily_returns*365)": mean_returns_percentage_stock* 365,
                "Alpha": ALPHA,
                "BETA": BETA,
                "std_deviation_stock": std_deviation_stock,
                "variance_stock": variance_stock ,
                "std_deviation_market": std_deviation_market,
                "variance_market" : variance_market,
                "co-relation (R^2)": co_relation,
                "unsystematic_risk" : unsystematic_risk ,

                }
            )
        table_1 = pd.DataFrame(results)
        self.table_1 = pd.DataFrame(results)
        self.window1_table=copy.deepcopy(self.table_1)
        print(self.window1_table)


        
    def update_indices_state(self, *args):
        global STOCK_EXCHANGE
        STOCK_EXCHANGE = self.exchange_var.get()
        
        if STOCK_EXCHANGE == "BSE":
            for widget in self.nse_indices_widgets:
                widget.config(state="disabled")
            for widget in self.bse_indices_widgets:
                widget.config(state="normal")
        elif STOCK_EXCHANGE == "NSE":
            for widget in self.bse_indices_widgets:
                widget.config(state="disabled")
            for widget in self.group_widgets:
                widget.config(state="disabled")
            for widget in self.nse_indices_widgets:
                widget.config(state="normal")
        else:
            for widget in self.bse_indices_widgets:
                widget.config(state="normal")
            for widget in self.nse_indices_widgets:
                widget.config(state="normal")
       
    def risk_free_return(self):
        new_window=tk.Toplevel(self)
        new_window.title("initial_inputs")
        new_window.geometry("1200x800")
        
        global RATE_RISK_FREE_RETURN_NSE
        
        main_frame = ttk.Frame(new_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
 
        # Risk Free Rate
        ttk.Label(input_frame, text="Risk Free Rate Of Return (%)", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.risk_free_entry = ttk.Entry(input_frame, font=("Arial", 12), width=20)
        self.risk_free_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Rate of Return
        ttk.Label(input_frame, text="Rate of Return", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.rate_of_return_combobox = ttk.Combobox(input_frame, values=["Average Return", "Expected Return"], font=("Arial", 12), width=20)
        self.rate_of_return_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.rate_of_return_combobox.set("Expected Return")
        
        # Ticker    
        ttk.Label(input_frame, text="Ticker", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.ticker_entry = ttk.Entry(input_frame, font=("Arial", 12), width=20)
        self.ticker_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_fun, style='my.TButton')
        self.delete_button.pack(side=tk.LEFT, padx=(10, 5))
        
        self.next_button = ttk.Button(button_frame, text="Next >", command=self.grid_view, style='my.TButton')
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(table_frame, style='Custom.Treeview')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Display the data
        self.display_table(self.window1_table)
        
        # Style configuration
        style = ttk.Style()
        style.configure('my.TButton', font=('Arial', 12))
        style.configure('Custom.Treeview', rowheight=25, font=('Arial', 11))
        style.configure('Custom.Treeview.Heading', font=('Arial', 12, 'bold'))

        # Display the data
        self.display_table(self.window1_table)
        
        #now remove the stocks with returns less than rate of risk free return and negative beta   
        try:
            RATE_RISK_FREE_RETURN_NSE = float(self.risk_free_entry.get())
        except ValueError:
            print("INVALID INPUT")
        self.table_1 = self.table_1[(self.table_1["returns_percentage"] > RATE_RISK_FREE_RETURN_NSE) & (self.table_1["BETA"] > 0)]
        self.table_1 =  self.table_1.sort_values(by="returns_percentage",ascending=False)
        #adding column excessive returns per beta
        self.table_1["excess returns"] = self.table_1["returns_percentage"] - RATE_RISK_FREE_RETURN_NSE
        self.table_1["excess returns to beta"] = (self.table_1["returns_percentage"] -  ( RATE_RISK_FREE_RETURN_NSE) ) / self.table_1["BETA"]

        #display the below dataframe in window_2_table_1
        window_2_table_1 = self.table_1[["NSETICKER","returns_percentage","excess returns","BETA","unsystematic_risk","excess returns to beta"]].copy(deep=True)
        
        
        cutoff_table = self.table_1[["NSETICKER","excess returns to beta","BETA","unsystematic_risk","returns_percentage","variance_market"]].sort_values(by="excess returns to beta",ascending=False)
        cutoff_table["(BETA^2)/(UNSYSTEMATIC_RISK)"] = (cutoff_table["BETA"]**2) / (cutoff_table["unsystematic_risk"])
        cutoff_table["cummulative_intermediate"] = cutoff_table["(BETA^2)/(UNSYSTEMATIC_RISK)"].cumsum()
        cutoff_table["treynor_ratio_times_A"] = cutoff_table["excess returns to beta"] * cutoff_table["(BETA^2)/(UNSYSTEMATIC_RISK)"]
        cutoff_table["cumulative_treynor"] = cutoff_table["treynor_ratio_times_A"].cumsum()
        cutoff_table["cutoff_point"] = (cutoff_table["variance_market"] * cutoff_table["cumulative_treynor"]) / (1 + (cutoff_table["variance_market"] * cutoff_table["cummulative_intermediate"]))
        #display the table below in window_2_table_2
        window_2_table_2 = cutoff_table.copy(deep=True)
        
        cutoff_max = cutoff_table["cutoff_point"].max()
        next_table =  cutoff_table[cutoff_table["excess returns to beta"] >= cutoff_max]
        next_table = next_table[["NSETICKER","returns_percentage","excess returns to beta","BETA","unsystematic_risk","cutoff_point"]]
        next_table["cutoff_max"] = cutoff_max
        
        weighted_table = next_table.copy(deep=True)
        weighted_table["excess_trenor"] = weighted_table["excess returns to beta"] - weighted_table["cutoff_max"]
        weighted_table["Z_i"] = weighted_table["excess_trenor"] * (weighted_table["BETA"]/weighted_table["unsystematic_risk"])

        #display this table in window_2_table_3
        window_2_table_3 = weighted_table[["NSETICKER","cutoff_point","cutoff_max","Z_i"]].copy(deep=True)

        weighted_table["weight"] = weighted_table["Z_i"] / weighted_table["Z_i"].sum()
        weighted_table["weight_percentage"] = weighted_table["weight"] * 100
        weighted_table["weighted_return"] = weighted_table["returns_percentage"] * weighted_table["weight_percentage"]

        #display the below table in window_2_table_4
        window_2_table_4 = weighted_table[["NSETICKER","returns_percentage","weight_percentage","weighted_return"]].copy(deep=True)

        weighted_table.sort_values(by="weight",ascending=False)
        TOTAL_RETURN_ON_PORTFOLIO = weighted_table["weighted_return"].sum()
        self.window_2_table_1 = window_2_table_1
        self.window_2_table_2 = window_2_table_2
        self.window_2_table_3 = window_2_table_3
        self.window_2_table_4 = window_2_table_4
        

    def display_table(self, df):
        # Clear the existing data in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        if df.empty:
            print("DataFrame is empty.")
            return
        # Set up columns
        self.tree["columns"] =  ["Select"]+list(df.columns)
        self.tree["show"] = "headings"

        # Set column headings
        self.tree.heading("Select", text="Select")
        self.tree.column("Select", width=50, anchor="center")
        for column in df.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)  # Adjust the width as needed

        # Add data to the treeview
        for index, row in df.iterrows():
            item = self.tree.insert("", "end", values=["[ ]"] + list(row))
            
        # Bind the checkbutton to update the tree
        self.tree.bind("<ButtonRelease-1>", self.on_click)
        
        
    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # The Select column
                item = self.tree.identify_row(event.y)
                current = self.tree.set(item, "Select")
                new_value = "[\u2713]" if current == "[ ]" else "[ ]"
                self.tree.set(item, "Select", new_value)
            
    def grid_view(self):
        new_window=tk.Toplevel(self)
        new_window.title("initial_inputs")
        new_window.geometry("1050x1050")
        print("table1")
        print(self.window_2_table_1)
        print("table2")
        print(self.window_2_table_2)
        print("table3")
        print(self.window_2_table_3)
        print("table4")
        print(self.window_2_table_4)
        # Create four frames for each table
        frames = [ttk.Frame(new_window) for _ in range(4)]
        for i, frame in enumerate(frames):
            row = i // 2
            col = i % 2
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            new_window.grid_rowconfigure(row, weight=1)
            new_window.grid_columnconfigure(col, weight=1)

        # Create and populate treeviews for each table
        tables = [self.window_2_table_1, self.window_2_table_2, self.window_2_table_3, self.window_2_table_4]
        titles = ["Table 1", "Table 2", "Table 3", "Table 4"]
        
        for frame, table, title in zip(frames, tables, titles):
        # Create a label for the table title
            ttk.Label(frame, text=title, font=("Arial", 12, "bold")).pack(pady=5)
            tree_frame = ttk.Frame(frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            # Create Treeview
            tree = ttk.Treeview(tree_frame)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Add vertical scrollbar
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=vsb.set)

            # Add horizontal scrollbar
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            tree.configure(xscrollcommand=hsb.set)

            # Set up columns
            tree["columns"] = list(table.columns)
            tree["show"] = "headings"

            # Set column headings
            for column in table.columns:
                tree.heading(column, text=column)
                tree.column(column, width=100)  # Adjust the width as needed

            # Add data to the treeview
            for _, row in table.iterrows():
                tree.insert("", "end", values=list(row))
                
            
            frame.pack_propagate(False)
            
            # Add a button at the bottom center
            button_frame = ttk.Frame(new_window)
            button_frame.grid(row=2, column=0, columnspan=2, pady=20)
    
            compare_button = ttk.Button(button_frame, text="Compare Portfolio Returns with Market", command=self.comparison)
            compare_button.pack()
        
    def delete_fun(self):
        # Get selected items with the checkmark
        selected_items = [item for item in self.tree.get_children() if self.tree.set(item, "Select") == "[\u2713]"]
        
        # Check if there are no selected items
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select rows to delete.")
            return
        
        # Ask for confirmation before deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected rows?")
        if confirm:
            # Get the BSETICKER values for the selected items
            selected_nsetickers = [self.tree.set(item, "NSETICKER") for item in selected_items]
            
            # Remove the selected tickers from table_1
            self.table_1 = self.table_1[~self.table_1["NSETICKER"].isin(selected_nsetickers)]
            
            # Update window_1_table with a deep copy of the modified table_1
            self.window1_table = copy.deepcopy(self.table_1)
            
            # Remove the selected items from the tree view
            for item in selected_items:
                self.tree.delete(item)
            
            # Show a success message
            messagebox.showinfo("Deletion Successful", f"{len(selected_items)} row(s) deleted.")

    def comparison(self):
        portfolio_stocks_and_weights = {row["NSETICKER"]: row["weight_percentage"] for index, row in self.window_2_table_4.iterrows()}
        
        # Adjust START_DATE
        START_DATE = self.START_DATE + timedelta(days=1)
        START_DATE = START_DATE.strftime("%Y-%m-%d")
        
        def get_stock_value(ticker: str, date: str, db_cursor=self.cursor, max_days: int = 365):
            DATE = datetime.strptime(date, "%Y-%m-%d").date()
            earliest_date = DATE - timedelta(days=max_days)
            current_date = DATE
            
            while current_date >= earliest_date:
                date_str = current_date.strftime("%Y-%m-%d")
                query = f"SELECT Close FROM mstr_nse_eod WHERE Date = '{date_str}' AND NSETICKER='{ticker}'"
                db_cursor.execute(query)
                result = db_cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    current_date -= timedelta(days=1)
            
            return None
        
        def make_portfolio(portfolio_with_weights: dict, start_date: str = START_DATE, db_cursor=self.cursor, portfolio_amount: int = 100000):
            portfolio = dict()
            for stock in portfolio_with_weights:
                amount_invested_in_stock = portfolio_amount * (portfolio_with_weights[stock]/100)
                stock_value_on_start_date = get_stock_value(stock, start_date, db_cursor=db_cursor)
                if stock_value_on_start_date is None:
                    print(stock, start_date, stock_value_on_start_date)
                    continue
                no_of_shares_of_stock = int(amount_invested_in_stock / stock_value_on_start_date)
                portfolio[stock] = no_of_shares_of_stock
            return portfolio
        
        def get_portfolio_value(date: str, portfolio_dict, db_cursor=self.cursor):
            values = []
            for stock in portfolio_dict:
                stock_value = get_stock_value(date=date, ticker=stock, db_cursor=db_cursor)
                total_value_of_stock = portfolio_dict[stock] * stock_value
                values.append(total_value_of_stock)
            value = np.array(values)
            return value.sum()
        
        def get_index_value(date:str, index_name: str = INDEX_TO_REGRESS_WITH_NSE, db_cursor=self.cursor, max_days:int = 365):
            DATE = datetime.strptime(date, "%Y-%m-%d").date()
            earliest_date = DATE - timedelta(days=max_days)
            current_date = DATE
            
            while current_date >= earliest_date:
                date_str = current_date.strftime("%Y-%m-%d")
                query = f"SELECT Close FROM mstr_nse_indexes_eod WHERE Date = '{date_str}' AND Index_name='{index_name}'"
                db_cursor.execute(query)
                result = db_cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    current_date -= timedelta(days=1)
            
            return None
        
        def calculate_portfolio_returns(start_date:str = START_DATE, end_date: str = self.END_DATE.strftime("%Y-%m-%d"), db_cursor=self.cursor, portfolio_dict=None):
            value_on_starting = get_portfolio_value(start_date, db_cursor=db_cursor, portfolio_dict=portfolio_dict)
            value_on_ending = get_portfolio_value(end_date, db_cursor=db_cursor, portfolio_dict=portfolio_dict)
            returns_percentage = ((value_on_ending-value_on_starting)/(value_on_starting))*100
            return returns_percentage
        
        def calculate_index_returns(start_date:str = START_DATE, end_date: str = self.END_DATE.strftime("%Y-%m-%d"), db_cursor=self.cursor, index_name: str = INDEX_TO_REGRESS_WITH_NSE):
            value_on_starting = get_index_value(start_date, db_cursor=db_cursor)
            value_on_ending = get_index_value(end_date, db_cursor=db_cursor)
            returns_percentage = ((value_on_ending-value_on_starting)/(value_on_starting))*100
            return returns_percentage
        
        def get_date_list(start_date:str = START_DATE, end_date:str = self.END_DATE.strftime("%Y-%m-%d"), date_format:str = "%Y-%m-%d"):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            return [(start_date + timedelta(days=x)).strftime(date_format) for x in range((end_date - start_date).days + 1)]
        
        def get_data(start_date:str = START_DATE, end_date: str = self.END_DATE.strftime("%Y-%m-%d"), portfolio_dict=None, db_cursor=self.cursor):
            dates = get_date_list(start_date, end_date)
            datewise_returns = []
            datewise_index_returns = []
            for date in dates:
                print(f"got data for index for date: {date}")
                datewise_returns.append(calculate_portfolio_returns(end_date=date, db_cursor=db_cursor, portfolio_dict=portfolio_dict))
                datewise_index_returns.append(calculate_index_returns(end_date=date, db_cursor=db_cursor))
            dates = pd.date_range(start=start_date, end=end_date, freq="D")
            datewise_returns = np.array(datewise_returns)
            datewise_index_returns = np.array(datewise_index_returns)
            return (dates, datewise_returns, datewise_index_returns)
        
        portfolio_dict = make_portfolio(portfolio_stocks_and_weights, START_DATE, self.cursor)
        dates, datewise_returns, datewise_index_returns = get_data(START_DATE, self.END_DATE.strftime("%Y-%m-%d"), portfolio_dict, self.cursor)
        print("DATES.............",dates)
        print("DATEWISE_RETURNS0\.............",datewise_returns)
        print("DATEWISE_INDEXES..................",datewise_index_returns)
        # Now you can use dates, datewise_returns, and datewise_index_returns to create a plot or display the results
        # For example:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, datewise_returns, label='Portfolio Returns')
        ax.plot(dates, datewise_index_returns, label='Index Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns (%)')
        ax.set_title('Portfolio Returns vs Index Returns')
        ax.legend()
        
        cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
        hline = ax.axhline(y=0, color='k', lw=0.8, ls='--')
        vline = ax.axvline(x=dates[0], color='k', lw=0.8, ls='--')
        
        text_box = ax.text(0.02, 0.98, '', transform=ax.transAxes, va='top', ha='left', 
                       bbox=dict(facecolor='white', edgecolor='none', alpha=0.65))
        
        def on_mouse_move(event):
            if event.inaxes:
                x, y = event.xdata, event.ydata
                date = mdates.num2date(x).strftime('%Y-%m-%d')
                hline.set_ydata([y,y])
                vline.set_xdata([x,x])
                text_box.set_text(f'Date: {date}\nReturns: {y:.2f}%')
                remove_annotation()
                fig.canvas.draw_idle()
                
        def on_click(event):
            global current_annotation
            if event.inaxes:
                remove_annotation()
                date = mdates.num2date(event.xdata).strftime('%Y-%m-%d')
                returns = event.ydata
                current_annotation=ax.annotate(f'Date: {date}\nReturns: {returns:.2f}%', 
                            xy=(event.xdata, event.ydata),
                            xytext=(10, 10), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                fig.canvas.draw()
                
        def remove_annotation():
            global current_annotation
            if current_annotation:
                current_annotation.remove()
                current_annotation = None
        fig.canvas.draw()  
        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        fig.canvas.mpl_connect('button_press_event', on_click)
        # Display the plot in a new Tkinter window
        
        def plot_results(ticker:str, range:tuple = (-10,10), precision:int = 100, no_of_bins_hist:int = 25):
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,6))
            
            axes[0].hist(self.df_512[ticker]["returns_percentage"], bins=no_of_bins_hist, edgecolor="black")
            axes[0].set_xlabel("returns percentage")
            axes[0].set_ylabel("frequency")
            
            mu = self.df_512[ticker]["returns_percentage"].mean()  # Mean
            sigma = self.df_512[ticker]["returns_percentage"].std()  # Standard deviation
            x = np.linspace(range[0], range[1], precision)
            
            pdf = norm.pdf(x, mu, sigma)
            
            axes[1].plot(x, pdf)
            axes[1].set_xlabel("returns_percentage")
            axes[1].set_ylabel("probability density")
            
            fig.suptitle(f"TICKER = {ticker}")
            plt.tight_layout()
            plt.show()
        
        def display_analysis():
            analysis_window = tk.Toplevel(self)
            analysis_window.title("Stock Analysis")

            # Create dropdown for stock selection
            stock_list = list(portfolio_stocks_and_weights.keys())
            selected_stock = tk.StringVar(analysis_window)
            selected_stock.set(stock_list[0])  # Set default value
            stock_dropdown = ttk.Combobox(analysis_window, textvariable=selected_stock, values=stock_list)
            stock_dropdown.pack(pady=10)

            # Create input fields for other parameters
            min_range = tk.Entry(analysis_window)
            min_range.insert(0, "-10")
            min_range.pack(pady=5)
            tk.Label(analysis_window, text="Min Range").pack()

            max_range = tk.Entry(analysis_window)
            max_range.insert(0, "10")
            max_range.pack(pady=5)
            tk.Label(analysis_window, text="Max Range").pack()

            precision = tk.Entry(analysis_window)
            precision.insert(0, "100")
            precision.pack(pady=5)
            tk.Label(analysis_window, text="Precision").pack()

            no_of_bins = tk.Entry(analysis_window)
            no_of_bins.insert(0, "25")
            no_of_bins.pack(pady=5)
            tk.Label(analysis_window, text="Number of Histogram Bins").pack()

            def run_analysis():
                ticker = selected_stock.get()
                range_tuple = (float(min_range.get()), float(max_range.get()))
                precision_value = int(precision.get())
                bins = int(no_of_bins.get())
                plot_results(ticker, range=range_tuple, precision=precision_value, no_of_bins_hist=bins)

            analyze_button = ttk.Button(analysis_window, text="Analyze", command=run_analysis)
            analyze_button.pack(pady=20)
            
        new_window = tk.Toplevel(self)
        new_window.title("Portfolio Comparison")
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both",expand=True)
        button_frame=tk.Frame(new_window)
        button_frame.pack(pady=20)
        analyze_button = ttk.Button(button_frame, text="analyze the portfolio", command=display_analysis)
        analyze_button.pack()