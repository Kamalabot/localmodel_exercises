import csv
from io import StringIO

def fix_broken_formulas(csv_data):
    """
    Processes CSV data to identify and correct formulas that fail due to 
    non-numeric or missing values in input columns (Quantity, Unit Price).
    The correction uses IFERROR logic simulation.
    """
    # Use StringIO to treat the string as a file
    csvfile = StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    print("--- Formula Error Handling Simulation ---")
    print("Goal: Calculate Total = Quantity * Unit Price, handling text/error values.")
    print("\nProposed Robust Formula Structure (for a new 'Corrected Total' column):")
    print("=IFERROR(Quantity * Unit_Price, \"Check Input\")")

    results = []
    
    for i, row in enumerate(reader):
        row_number = i + 2 # Start counting from row 2 (after header)
        item = row['Item'].strip()
        quantity_raw = row['Quantity'].strip()
        price_raw = row['Unit Price'].strip()
        
        # Attempt to convert inputs to numbers, handling common errors like 'N/A', 'None', or text.
        try:
            # Clean up known non-numeric placeholders for calculation attempt
            quantity = float(str(quantity_raw).replace('None', '').replace('N/A', '') or 0)
            price = float(str(price_raw).replace('Error', '').replace('N/A', '') or 0)
            
            # Calculate the corrected total
            corrected_total = round(quantity * price, 2)
            print(f"Row {row_number} ({item}): Success. Corrected Total: ${corrected_total:.2f}")

        except ValueError:
            # This catches cases where the cleaned string is still not a valid float (e.g., empty or pure text)
            print(f"Row {row_number} ({item}): Failed to calculate. Input data ('{quantity_raw}', '{price_raw}') contains non-numeric/unfixable errors.")

    return "Simulation complete. Check the console output for detailed results."

# --- Example Usage with the data from Exercise 6 ---
csv_data = """Item,Quantity,Unit Price,Total
Widget A,10,15,150
Widget B,5,N/A,#VALUE!
Widget C,12,20,240
Widget D,None,30,#VALUE!
Widget E,8,10,80
Widget F,15,Error,#VALUE!
Widget G,20,5,100"""

print("--- Running Formula Fix Simulation ---")
fix_broken_formulas(csv_data)