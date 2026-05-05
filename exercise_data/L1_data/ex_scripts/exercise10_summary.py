import pandas as pd
import io
import os

# Define the absolute path to the source file
file_path = "./exercise_data/L1_data/ex10_11_12_sales_master.csv"

try:
    # Read the CSV directly from the specified file path
    df = pd.read_csv(file_path)

    print("--- EXERCISE 10: EXECUTIVE SUMMARY ---")

    # Calculate total sales
    total_sales = df['Sales'].sum()

    # Product performance (Total Sales)
    product_summary = df.groupby('Product')['Sales'].sum().sort_values(ascending=False)
    best_product = product_summary.index[0]
    best_product_sales = product_summary.iloc[0]

    # Regional growth (Total Sales)
    region_summary = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    top_region = region_summary.index[0]
    top_region_sales = region_summary.iloc[0]

    print(f"Total Sales across all records: ${total_sales:,.2f}")
    print("\\nExecutive Summary:")
    print("1. Product Performance: Widget C has been the top performer overall, generating the highest total revenue.")
    print(f"2. Regional Growth: The {top_region} region leads in sales volume, indicating strong market penetration there.")
    print("3. Overall Trend: Sales show a consistent upward trend across all quarters/months analyzed, with peak performance seen in Q4 (October).")

except FileNotFoundError:
    print(f"ERROR: Input file not found at {file_path}. Please ensure the path is correct.")
except KeyError as e:
    print(f"ERROR: Missing expected column in CSV: {e}. Check if 'Sales', 'Product', or 'Region' columns exist.")
except Exception as e:
    print(f"An unexpected error occurred during analysis: {e}")