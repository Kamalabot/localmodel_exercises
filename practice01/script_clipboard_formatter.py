import re

def format_clipboard_data(file_path):
    """
    Reads messy, delimited text (simulating clipboard paste) and formats it 
    into a clean table structure suitable for Excel.
    This function assumes the data has consistent column structures 
    but inconsistent delimiters/spacing.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return "Error: The file was not found."

    # --- Cleaning Logic based on the provided sample data structure ---
    
    # 1. Split into lines and clean up excessive whitespace/newlines
    lines = [line.strip() for line in content.split('\\n') if line.strip()]
    if not lines:
        return "Error: No data found in the file."

    # The first line is assumed to be the header row
    header_raw = lines[0]
    # Simple heuristic to clean headers (assuming they are separated by tabs/multiple spaces)
    headers = [h.strip() for h in re.split(r'\s{2,}|[\t]', header_raw) if h.strip()]

    cleaned_data = []
    
    # Process data rows starting from the second line
    for i, line in enumerate(lines[1:]):
        row_data = {}
        
        # Use a robust regex to split by common delimiters (tab or multiple spaces)
        parts = [p.strip() for p in re.split(r'\s{2,}|[\t]', line) if p.strip()]
        
        if len(parts) != len(headers):
            # If column count doesn't match header count, we might have a merged cell issue (like SKU-004 example)
            print(f"Warning: Row {i+2} has {len(parts)} columns but expected {len(headers)}. Attempting best effort.")
        
        # Map parts to headers based on the assumption of column order
        for j in range(min(len(parts), len(headers))):
            header = headers[j]
            value = parts[j]
            row_data[header] = value

        cleaned_data.append(row_data)

    # --- Formatting Output for Presentation (Markdown Table) ---
    if not cleaned_data:
        return "Could not parse any structured data from the input."

    # Determine final keys based on the first successful row's structure
    final_headers = list(cleaned_data[0].keys())
    
    markdown_table = "| " + " | ".join(final_headers) + " |\n"
    markdown_table += "|---" * len(final_headers) + "|\n"

    for row in cleaned_data:
        row_values = []
        for header in final_headers:
            # Use the value found for that specific header, or an empty string if missing
            value = str(row.get(header, "")).replace("|", "\\|") # Escape pipe characters
            row_values.append(value)
        markdown_table += "| " + " | ".join(row_values) + " |\n"

    return markdown_table

if __name__ == "__main__":
    # IMPORTANT: Update this path to point to the actual file you want to test
    file_to_test = "temp_clipboard_data.txt" 
    
    print(f"--- Processing data from: {file_to_test} ---")
    formatted_table = format_clipboard_data(file_to_test)
    
    print("\n--- Formatted Excel Table Output (Markdown Format) ---\n")
    print(formatted_table)

    # To save this structured data to a new file:
    output_filename = "formatted_clipboard_summary.txt"
    with open(output_filename, "w", encoding="utf-8") as out_f:
        out_f.write("--- Formatted Data ---\n\n")
        out_f.write(formatted_table)
    print(f"\nSummary saved to {output_filename} in the current directory.")