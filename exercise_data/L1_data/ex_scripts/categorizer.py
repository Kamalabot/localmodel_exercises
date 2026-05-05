import csv
from io import StringIO

def categorize_transaction(description):
    """
    Assigns a category based on keywords found in the transaction description.
    This simulates an LLM's ability to perform categorization.
    """
    desc = description.lower()
    
    # Define keyword mappings: Category -> [keywords]
    category_map = {
        "Food & Dining": ["starbucks", "chipotle", "whole foods", "safeway", "restaurant", "groceries"],
        "Transportation": ["uber", "lyft", "shell", "chevron", "airport"],
        "Utilities/Bills": ["pg&e", "comcast", "netflix", "internet", "utility bill"],
        "Shopping/Services": ["amazon.com", "apple.com", "membership"]
    }

    for category, keywords in category_map.items():
        for keyword in keywords:
            if keyword in desc:
                return category
    
    # Default fallback category
    return "Miscellaneous"

def process_transactions(csv_data):
    """
    Reads transaction data and adds a 'Category' column based on the description.
    """
    csvfile = StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    output_rows = []
    
    for i, row in enumerate(reader):
        description = row['Description'].strip()
        category = categorize_transaction(description)
        
        # Create a new dictionary for the output row
        new_row = {
            'Date': row['Date'],
            'Description': description,
            'Amount': row['Amount'],
            'Category': category # The newly added field
        }
        output_rows.append(new_row)

    # Format the output back into CSV string format
    fieldnames = ['Date', 'Description', 'Amount', 'Category']
    output_csv_content = ",".join(fieldnames) + "\n"
    for row in output_rows:
        # Escape quotes and join fields for clean CSV writing
        escaped_row = [str(item).replace('"', '""') for item in row.values()]
        output_csv_content += ",".join(escaped_row) + "\n"
    
    return output_csv_content

# --- Example Usage with the data from Exercise 9 ---
csv_data = """Date,Description,Amount
2024-01-01,Starbucks Coffee #442,6.50
2024-01-02,Uber Trip - San Francisco,24.30
2024-01-02,PG&E Utility Bill,145.00
2024-01-03,Whole Foods Market,88.20
2024-01-04,Shell Gas Station,55.00
2024-01-05,Netflix.com Subscription,15.99
2024-01-05,Amazon.com - Electronics,129.00
2024-01-06,Chipotle Mexican Grill,14.50
2024-01-07,Lyft Ride - Airport,32.00
2024-01-08,Comcast Xfinity Internet,89.99
2024-01-09,Apple.com - iCloud Storage,2.99
2024-01-10,Chevron Fuel,62.40
2024-01-11,Safeway Groceries,74.15
2024-01-12,Planet Fitness Membership,25.00
2024-01-13,DoorDash - Sushi Zen,42.10"""

output = process_transactions(csv_data)
print("--- Generated CSV Content ---")
print(output)