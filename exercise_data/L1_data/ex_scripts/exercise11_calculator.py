import pandas as pd

# Define the path to the data file
DATA_FILE = "exercise_data/L1_data/ex10_11_12_sales_master.csv"
OUTPUT_FILE = "Adjusted_Profit_Results.csv"

def calculate_adjusted_profit(input_path: str, output_path: str):
    """
    Loads sales data from a CSV, calculates the Adjusted Profit based on 
    a 5% price increase and constant costs, and saves the result.
    """
    try:
        # Load the entire dataset using pandas
        df = pd.read_csv(input_path)
        print(f"Successfully loaded data from: {input_path}")

        # --- Calculation Logic for Exercise 11 ---
        
        # 1. Calculate the new Price (Price * 1.05)
        # We use .astype(float) to ensure calculations are done numerically, 
        # as pandas might read currency columns as strings initially.
        df['New_Price'] = df['Price'].astype(float) * 1.05
        
        # 2. Calculate Adjusted Profit: (New Price) - Cost
        # Costs remain the same per the prompt.
        df['Adjusted Profit'] = df['New_Price'] - df['Cost'].astype(float)

        # --- Output Preparation ---
        
        # Select relevant columns for the final output, including the new one
        output_columns = [
            'Date', 'Region', 'Product', 'Price', 'Cost', 'Units', 'Sales', 
            'New_Price', 'Adjusted Profit' # Including intermediate steps for verification
        ]
        df_output = df[output_columns]

        # Save the resulting DataFrame to a new CSV file
        df_output.to_csv(output_path, index=False)
        print(f"Calculation complete. Results saved successfully to: {output_path}")

    except FileNotFoundError:
        print(f"ERROR: Input file not found at {input_path}. Please check the path.")
    except KeyError as e:
        print(f"ERROR: Missing expected column in CSV: {e}. Check if 'Price' and 'Cost' columns exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # The script assumes the data file is accessible relative to where it runs.
    calculate_adjusted_profit(DATA_FILE, OUTPUT_FILE)