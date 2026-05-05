import csv
from io import StringIO

def calculate_discount(csv_data):
    """
    Processes CSV data to apply a conditional discount calculation.
    Formula Logic: IF Status is 'Gold' AND Total > 500, THEN Discount = Total * 0.15, ELSE 0.
    """
    # Use StringIO to treat the string as a file
    csvfile = StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    results = []
    print("--- Formula Logic Simulation ---")
    print("Formula structure: IF(AND(Status=\"Gold\", Total>500), Total*0.15, 0)")
    print("\n--- Row-by-Row Evaluation ---")

    for i, row in enumerate(reader):
        row_number = i + 2 # Start counting from row 2 (after header)
        try:
            status = row['Status']
            total = float(row['Total'])
        except ValueError:
            print(f"Skipping Row {row_number}: Could not convert Total to float.")
            continue

        # The core logic check
        if status == 'Gold' and total > 500:
            discount = total * 0.15
            result_str = f"Row {row_number} ({status}, ${total:.2f}): Condition MET. Discount calculated: ${discount:.2f}"
            results.append(result_str)
        else:
            result_str = f"Row {row_number} ({status}, ${total:.2f}): Condition NOT met. Discount is 0."
            results.append(result_str)
    
    return "\n".join(results)

# --- Example Usage with the data from Exercise 4 ---
csv_data = """Status,Total,Customer ID
Gold,600,CUST101
Silver,300,CUST102
Gold,450,CUST103
Bronze,100,CUST104
Gold,1200,CUST105
Silver,800,CUST106
Bronze,50,CUST107
Gold,510,CUST108
Silver,200,CUST109
Gold,750,CUST110"""

output = calculate_discount(csv_data)
print(output)