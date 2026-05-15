import re


def extract_profile_data(file_path):
    """
    Reads an unstructured text file and extracts Name, Email, and Company
    using regex patterns, simulating the logic from Exercise 1.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return "Error: The file was not found."

    # Regex patterns based on the structure of ex1_messy_profile.txt
    name_match = re.search(r"Name:\s*(.*)", content)
    email_match = re.search(
        r"Contact Info:.*?([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})", content
    )
    # Company is tricky; we'll look for a role description to infer the company name.
    company_match = re.search(
        r"Current Role:.*?\s+at\s+(.*?)\s*$", content, re.MULTILINE
    )

    name = name_match.group(1).strip() if name_match else "N/A"
    email = email_match.group(1).strip() if email_match else "N/A"
    company = company_match.group(1).strip() if company_match else "N/A"

    # Return results in a structured format (e.g., dictionary or list)
    return {"Name": name, "Email": email, "Company": company}


if __name__ == "__main__":
    # IMPORTANT: Update this path to point to the actual file you want to test
    file_to_test = "D:/gitfolders/localmodel_exercises/exercise_data/L1_data/ex1_messy_profile.txt"

    extracted_data = extract_profile_data(file_to_test)

    print("--- Extraction Successful ---")
    for key, value in extracted_data.items():
        print(f"{key}: {value}")

    # To save this structured data to a new file:
    output_filename = "extracted_profile_summary.txt"
    with open(output_filename, "w", encoding="utf-8") as out_f:
        out_f.write("--- Extracted Data ---\n")
        for key, value in extracted_data.items():
            out_f.write(f"{key}: {value}\n")
    print(f"\nSummary saved to {output_filename} in the current directory.")
