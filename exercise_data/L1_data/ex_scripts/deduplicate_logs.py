import csv
from io import StringIO
from datetime import datetime

def deduplicate_logs(csv_data):
    """
    Processes user log data to find duplicates based on User ID and keeps the row 
    with the most recent 'Last Login'. If dates are identical, it prioritizes 'Active' status.
    """
    # Use StringIO to treat the string as a file
    csvfile = StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    # Dictionary to hold the best record found so far for each User ID: {user_id: best_record}
    best_records = {}

    for i, row in enumerate(reader):
        try:
            user_id = row['User ID'].strip()
            login_date_str = row['Last Login'].strip()
            status = row['Status'].strip()
            
            # Attempt to parse the date. Assuming a standard format for comparison.
            # In a real scenario, we'd need to know the exact input format.
            try:
                login_date = datetime.strptime(login_date_str, '%Y-%m-%d') # Example format
            except ValueError:
                 # Fallback if date parsing fails (e.g., using a simpler comparison)
                login_date = login_date_str 

            current_record = {
                'User ID': user_id,
                'Date': login_date_str,
                'Status': status,
                'Record': row # Keep the original dictionary for output
            }

            if user_id not in best_records:
                best_records[user_id] = current_record
            else:
                existing_record = best_records[user_id]
                
                # 1. Compare Dates (Most recent wins)
                # NOTE: This comparison assumes date strings are comparable lexicographically if datetime fails.
                if login_date > existing_record['Date']:
                    best_records[user_id] = current_record
                elif login_date == existing_record['Date']:
                    # 2. Dates are the same, prioritize 'Active' status
                    if status == 'Active' and existing_record['Status'] != 'Active':
                        best_records[user_id] = current_record
                    # If both are Active or both are not Active, we keep the existing one (arbitrary tie-breaker)

        except KeyError as e:
            print(f"Error processing row {i+2}: Missing expected column in CSV data: {e}")
            continue

    # Format the final output list
    final_list = []
    for user_id, record in best_records.items():
        final_list.append({
            'User ID': record['Record']['User ID'],
            'Last Login': record['Date'],
            'Status': record['Record']['Status']
        })

    return final_list

# --- Example Usage with the data from Exercise 8 ---
csv_data = """User ID,Date,Status
U100,2024-05-01,Active
U200,2024-05-10,Inactive
U100,2024-05-15,Active
U300,2024-06-01,Active
U200,2024-05-10,Active
U100,2024-05-01,Inactive"""

final_records = deduplicate_logs(csv_data)

print("\n--- Final Deduplicated Records (User ID | Last Login | Status) ---")
for record in final_records:
    print(f"{record['User ID']} | {record['Last Login']} | {record['Status']}")