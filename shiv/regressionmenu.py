import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkcalendar import DateEntry


class RegressionMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.add_command(label="Regression",command=self.regression)
        
    def regression(self):
        new_window=tk.Toplevel(self)
        new_window.title("Solutions & Strategies [Matrix]")
        new_window.geometry("1050x1050")
        
        independent_variable_selection_window = ttk.LabelFrame(new_window, text="Independent Variable Seletion Window")
        independent_variable_selection_window.grid(row=0,column=0,columnspan=3,padx=10,pady=10)
        
        regression_equation=ttk.LabelFrame(new_window,text="Regression Equation")
        regression_equation.grid(row=1,column=0,padx=10,pady=10)
        
        dependent_variable_selection_window=ttk.LabelFrame(new_window,text="Dependent Variable Selection Window")
        dependent_variable_selection_window.grid(row=1,column=1,padx=10,pady=10)
        
        dependent_variable_label=ttk.Label(dependent_variable_selection_window,text="Select Dependent Variable")
        dependent_variable_label.grid(row=0,column=0,padx=10,pady=10)
        self.varible_combobox=ttk.Combobox(dependent_variable_selection_window,values=[1,2])
        #empty list here
        self.varible_combobox.grid(row=0,column=1,padx=10,pady=10)
        self.varible_combobox.set("dependent variable selection")
        
        run_on_label=ttk.Label(dependent_variable_selection_window,text="I want to run on")
        run_on_label.grid(row=1,column=0,padx=10,pady=10)
        self.run_combobox=ttk.Combobox(dependent_variable_selection_window,values=['Close','High','Low','Open'])
        self.run_combobox.set("Close")
        
        self.change_variable=ttk.Button(dependent_variable_selection_window,text="Change Independent Variable",command=self.change_independent_variable)
        self.change_variable.grid(row=2, column=1, padx=5, pady=5)
        
        self.confirmy=ttk.Button(dependent_variable_selection_window,text="Confirm Y",command=self.confirm_Y)
        self.confirmy.grid(row=2,column=2,padx=5,pady=5)
        
        
        security_selection_window=ttk.LabelFrame(new_window,text="Security Selection Window")
        security_selection_window.grid(row=1,column=2,padx=10,pady=10)
        
        company_name_label=ttk.Label(security_selection_window,text="Company Name")
        company_name_label.grid(row=0,column=0,padx=10,pady=10)
        self.company_combobox = ttk.Combobox(security_selection_window, values=[])
        #empty list here.
        self.company_combobox.grid(row=1, column=1,columnspan=2, padx=10, pady=10)
        self.company_combobox.set("select company")
        
        choose_exchange_label=ttk.Label(security_selection_window,text="Choose Exchange")
        choose_exchange_label.grid(row=1,column=0,padx=10,pady=10)
        self.rate_of_return_combobox = ttk.Combobox(security_selection_window, values=["BSE", "NSE"])
        self.rate_of_return_combobox.grid(row=1, column=1,columnspan=2, padx=10, pady=10)
        self.rate_of_return_combobox.set("BSE")
        
        return_checkbutton = ttk.Checkbutton(security_selection_window, text="Return")
        return_checkbutton.grid(row=2, column=0, padx=10, pady=10)
        
        self.add_button = ttk.Button(security_selection_window, text="Add", command=self.addd)
        self.add_button.grid(row=2, column=1, padx=5, pady=5)
        
        self.done_button = ttk.Button(security_selection_window, text="Done", command=self.donee)
        self.done_button.grid(row=2, column=2, padx=5, pady=5)
        
        time_period_selection_window=ttk.LabelFrame(new_window,text="Time Period Selection Window")
        time_period_selection_window.grid(row=2,column=1,padx=10,pady=10)

        ttk.Label(time_period_selection_window, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.start_date_entry = DateEntry(time_period_selection_window, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(time_period_selection_window, text="End Date:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.end_date_entry = DateEntry(time_period_selection_window, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(time_period_selection_window, text="Interval:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.interval_entry = ttk.Entry(time_period_selection_window)
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.calculate_bias = ttk.Button(time_period_selection_window, text="Calculate Bias", command=self.calculate_biass)
        self.calculate_bias.grid(row=3, column=0, padx=5, pady=5)
        
        self.simulate_numbers_button = ttk.Button(time_period_selection_window, text="Simulate The Numbers", command=self.simulate_numbers)
        self.simulate_numbers_button.grid(row=3, column=1, padx=5, pady=5)
        
    def calculate_biass(self):
        print("bias calculated")
        
        
    def simulate_numbers(self):
        print("simulate the numbers")
        
    def addd(self):
        print("add")
        
    def donee(self):
        print("done")
        
    def change_independent_variable(self):
        print("change independent variable")
        
    def confirm_Y(self):
        print("confirm Y")