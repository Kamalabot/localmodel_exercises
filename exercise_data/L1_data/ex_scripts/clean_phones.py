import csv
from io import StringIO
import re

def clean_and_format_phone(raw_number):
    """
    Cleans a raw phone number string by stripping all non-digit characters 
    and reformatting the last 10 digits into (XXX) XXX-XXXX format.
    """
    # 1. Strip all non-digit characters
    digits = re.sub(r'\D', '', str(raw_number)).strip()
    
    # Check if we have at least 10 digits (assuming US format for the target)
    if len(digits) < 10:
        return "ERROR: Too few digits"

    # Take the last 10 digits to enforce the target structure
    ten_digits = digits[-10:]
    
    # 2. Reformat to (XXX) XXX-XXXX
    area_code = ten_digits[0:3]
    prefix = ten_digits[3:6]
    line_number = ten_digits[6:10]
    
    return f"({area_code}) {prefix}-{line_number}"

def process_phone_csv(input_csv_data):
    """
    Reads phone numbers from a CSV string and returns the cleaned data 
    as a new CSV formatted string.
    """
    # Use StringIO to treat the string as a file
    csvfile = StringIO(input_csv_data)
    reader = csv.DictReader(csvfile)

    output_rows = []
    
    for i, row in enumerate(reader):
        raw_number = row['Raw Phone Numbers']
        formatted_number = clean_and_format_phone(raw_number)
        output_rows.append((raw_number, formatted_number))

    # Format the output back into CSV string format
    output_csv_content = "Raw Phone Numbers,Formatted Number\n"
    for raw, formatted in output_rows:
        output_csv_content += f'"{raw}","{formatted}"\n'
        
    return output_csv_content

# --- Example Usage with the data from Exercise 5 ---
input_csv_data = """Raw Phone Numbers
1234567890
(987) 654-3210
555.123.4567
+1-212-555-0199
444 555 6666
(202)-555-0143
8005551212
917.555.0110
+1 415 555 2671
(718) 555-0192"""

output = process_phone_csv(input_csv_data)
print("--- Generated CSV Content ---")
print(output.strip())