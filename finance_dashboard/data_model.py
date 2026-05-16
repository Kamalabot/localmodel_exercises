import os
import pandas as pd
from datetime import datetime

DATA_DIR = r"D:\gitFolders\localmodel_exercises\exercise_data\accounts_data"

class DataModel:
    def __init__(self):
        self.ap_df = pd.DataFrame()
        self.ar_df = pd.DataFrame()
        self.budget_df = pd.DataFrame()
        self.expense_df = pd.DataFrame()
        self.gl_df = pd.DataFrame()
        self.load_data()
        
    def load_data(self):
        try:
            self.ap_df = pd.read_excel(os.path.join(DATA_DIR, "Accounts-Payable.xlsx"))
            self.ar_df = pd.read_excel(os.path.join(DATA_DIR, "Accounts-Receivable.xlsx"))
            self.budget_df = pd.read_excel(os.path.join(DATA_DIR, "Budget-Forecast.xlsx"))
            self.expense_df = pd.read_excel(os.path.join(DATA_DIR, "Expense-Claims.xlsx"))
            self.gl_df = pd.read_excel(os.path.join(DATA_DIR, "General-Ledger.xlsx"))
            
            # Ensure date columns are parsed correctly
            date_cols = ['InvoiceDate', 'DueDate', 'PaidDate', 'ReceivedDate', 'SubmitDate', 'PayDate', 'TxnDate']
            for df in [self.ap_df, self.ar_df, self.expense_df, self.gl_df]:
                for col in df.columns:
                    if col in date_cols:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_past_due_ap(self):
        """Return Accounts Payable items that are past due and not paid."""
        if self.ap_df.empty: return pd.DataFrame()
        today = pd.Timestamp(datetime.now().date())
        # Not fully paid
        unpaid = self.ap_df[self.ap_df['Status'].isin(['Open', 'Partial'])]
        past_due = unpaid[unpaid['DueDate'] < today]
        return past_due
        
    def get_past_due_ar(self):
        """Return Accounts Receivable items that are past due and not received."""
        if self.ar_df.empty: return pd.DataFrame()
        today = pd.Timestamp(datetime.now().date())
        unpaid = self.ar_df[self.ar_df['Status'].isin(['Open', 'Partial'])]
        past_due = unpaid[unpaid['DueDate'] < today]
        return past_due

    def get_pending_expenses(self):
        """Return Expense Claims that are submitted but not yet paid."""
        if self.expense_df.empty: return pd.DataFrame()
        return self.expense_df[self.expense_df['Status'] == 'Submitted']
        
    def export_to_excel(self, df, filepath):
        """Export a given dataframe to an Excel file."""
        try:
            df.to_excel(filepath, index=False)
            return True, "Export successful!"
        except Exception as e:
            return False, f"Export failed: {e}"
