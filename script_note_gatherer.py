import re

def extract_task_list(file_path):
    """
    Reads unstructured notes from a file and extracts tasks, status, and priority.
    This simulates creating a structured task list in Excel.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return "Error: The source file was not found at the specified path."

    # Regex to capture task description, status, and priority from lines like:
    # - Task description... Status: X. Priority: Y.
    # This pattern is designed to be flexible but requires clear markers.
    task_pattern = re.compile(r"-\s*(.*?)\s*Status:\s*(\w+).*?Priority:\s*(\w+)", re.IGNORECASE)

    extracted_tasks = []
    
    # Since the structure is inconsistent (some lines might miss Status/Priority), 
    # we will process line by line and use a more forgiving extraction method.
    lines = [line.strip() for line in content.split('\\n') if line.strip()]

    for line in lines:
        task_info = {
            "Task Description": "",
            "Status": "Unknown",
            "Priority": "Unknown"
        }
        
        # 1. Extract Priority (most reliable marker)
        priority_match = re.search(r"Priority:\s*(\w+)", line, re.IGNORECASE)
        if priority_match:
            task_info["Priority"] = priority_match.group(1).capitalize()

        # 2. Extract Status (second most reliable marker)
        status_match = re.search(r"Status:\s*(\w+)", line, re.IGNORECASE)
        if status_match:
            task_info["Status"] = status_match.group(1).capitalize()

        # 3. Extract Task Description (everything before the first marker or the whole line if no markers found)
        description = line
        if priority_match:
            # Truncate description to remove the known markers for cleaner output
            start_index = max(line.lower().find("status:"), line.lower().find("priority:"))
            if start_index != -1:
                description = line[:start_index].strip()
        elif status_match:
             # If only status is found, truncate before it
            start_index = line.lower().find("status:")
            if start_index != -1:
                 description = line[:start_index].strip()

        task_info["Task Description"] = description.replace('-', '').strip()


        # Final check to ensure we captured something meaningful
        if task_info["Task Description"] and task_info["Status"] != "Unknown" or task_info["Priority"] != "Unknown":
            extracted_tasks.append(task_info)

    return extracted_tasks

if __name__ == "__main__":
    # IMPORTANT: Update this path to point to the actual file you want to test
    source_file = "exercise_data/L1_data/ex3_unstructured_notes.txt" 
    
    print(f"--- Analyzing notes from: {source_file} ---")
    tasks = extract_task_list(source_file)

    if isinstance(tasks, str):
        print(tasks)
    else:
        # Outputting results in a clean Markdown table format for easy copy/paste into Excel
        headers = ["Task Description", "Status", "Priority"]
        markdown_table = "| " + " | ".join(headers) + " |\n"
        markdown_table += "|---" * len(headers) + "|\n"

        for task in tasks:
            row = [
                task["Task Description"], 
                task["Status"], 
                task["Priority"]
            ]
            markdown_table += "| " + " | ".join(row) + " |\n"
        
        print("\n--- Structured Task List (Markdown Format) ---\n")
        print(markdown_table)

        # Saving the structured output to a file in practice01/
        output_filename = "practice01/structured_task_list.txt"
        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write("--- Structured Task List ---\n\n")
            out_f.write(markdown_table)
        print(f"\nSummary saved to {output_filename} in the practice01 directory.")