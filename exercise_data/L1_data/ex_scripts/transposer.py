import csv
from io import StringIO

def complex_transposer(csv_data):
    """
    Processes data from a list containing Name, Dept, Role, and Allocation (%).
    It transforms the flat list into a matrix/dictionary structure where 
    Departments are rows, Project Roles are columns, and cells show the sum of Allocation %.
    """
    # Use StringIO to treat the string as a file
    csvfile = StringIO(csv_data)
    reader = csv.DictReader(csvfile)

    # Initialize the structure: {Department: {Role: Total_Allocation}}
    department_matrix = {}

    for i, row in enumerate(reader):
        try:
            name = row['Name'].strip()
            dept = row['Dept'].strip()
            role = row['Role'].strip()
            # Clean up allocation percentage (remove % and convert to float)
            allocation_str = row['Allocation'].strip().replace('%', '')
            allocation = float(allocation_str)
        except KeyError as e:
            print(f"Error: Missing expected column in CSV data: {e}")
            return "Failed to process due to missing columns."
        except ValueError:
            print(f"Skipping row {i+2}: Could not convert allocation '{row.get('Allocation')}' to float.")
            continue

        # Initialize department if it doesn't exist
        if dept not in department_matrix:
            department_matrix[dept] = {}
        
        # Accumulate the allocation for the specific role within that department
        current_role_total = department_matrix[dept].get(role, 0.0)
        department_matrix[dept][role] = round(current_role_total + allocation, 2)

    return department_matrix

# --- Example Usage with the data from Exercise 7 ---
csv_data = """Name,Dept,Role,Allocation
Alice,Engineering,Backend,30%
Bob,Marketing,Content,50%
Charlie,Engineering,Frontend,40%
David,Sales,Lead Gen,20%
Eve,Marketing,SEO,60%
Frank,Engineering,Backend,10%"""

matrix = complex_transposer(csv_data)

print("\n--- Transposed Matrix (Department -> {Role: Total Allocation %}) ---")
for dept, roles in matrix.items():
    print(f"\n{dept}:")
    # Print the role/allocation pairs nicely
    formatted_roles = ", ".join([f"{role}: {alloc}%" for role, alloc in roles.items()])
    print(f"  {formatted_roles}")

