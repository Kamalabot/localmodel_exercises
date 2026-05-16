import os
import pandas as pd

data_dir = r"D:\gitFolders\localmodel_exercises\exercise_data\accounts_data"
files = [
    "Accounts-Payable.xlsx",
    "Accounts-Receivable.xlsx",
    "Budget-Forecast.xlsx",
    "Expense-Claims.xlsx",
    "General-Ledger.xlsx"
]

for file in files:
    path = os.path.join(data_dir, file)
    print(f"--- {file} ---")
    try:
        df = pd.read_excel(path)
        print("Columns:", list(df.columns))
        print("Shape:", df.shape)
        print("Head:")
        print(df.head(2))
    except Exception as e:
        print(f"Error reading {file}: {e}")
    print("\n")
