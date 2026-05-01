# master_orchestrator.py
"""
Master Orchestration Script for Local Model Exercises Curriculum.

This script serves as the central skeleton to structure and run all exercises 
from Level 1 through Level 3. It is NOT a complete solution, but a framework 
to guide you in implementing the logic for each module sequentially.

To run this successfully, you must:
1. Install all required libraries (see setup instructions).
2. Implement the specific logic within the placeholder functions.
"""

import os
import sqlite3
import pandas as pd
# Import necessary external libraries here as you implement them
# Example: from pdfplumber import open_pdf 
# Example: from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
DATA_DIR = "exercise_data"
DB_NAME = "master_exercises.db"

def setup_environment():
    """Checks for required libraries and sets up the database."""
    print("="*60)
    print("🚀 STARTING MASTER ORCHESTRATOR SETUP")
    print("="*60)
    
    # 1. Library Check (Requires manual pip install for most)
    required_libs = [
        "pandas", "sqlite3", "pdfplumber", "playwright", "beautifulsoup4"
    ]
    print("\n[!] IMPORTANT: Please ensure all required libraries are installed:")
    print(f"    pip install pandas sqlite3 pdfplumber playwright beautifulsoup4")
    print("    And run 'playwright install' in your terminal.")

    # 2. Database Setup (For Level 3 exercises)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Create a basic table to test connectivity for L3/M2
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Projects (
                ProjectID INTEGER PRIMARY KEY,
                ProjectName TEXT UNIQUE,
                CostCenterID TEXT,
                LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print(f"\n✅ Database '{DB_NAME}' initialized successfully.")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

# ==============================================================================
# LEVEL 1: EXCEL & PI FOR EXCEL (Data Cleaning & Formulas)
# Focus: Pandas for data manipulation, simulating Excel logic.
# ==============================================================================
def run_l1_excel_logic():
    """Handles exercises from L1_Excel_Exercises.md."""
    print("\n" + "="*20 + " LEVEL 1: EXCEL LOGIC SIMULATION " + "="*20)
    
    # --- Exercise 1-3 (Text Extraction/Cleaning) ---
    print("-> Running Data Scavenger (L1 Ex 1-3)...")
    try:
        # Placeholder for reading messy text files and using LLM prompts via API call
        # Example: df = pd.read_csv(os.path.join(DATA_DIR, "L1_data", "ex1_messy_profile.txt"))
        print("   [Placeholder]: Implement logic to use an external LLM API call here.")
    except FileNotFoundError:
        pass

    # --- Exercise 4-6 (Formula Logic) ---
    print("\n-> Running Formula Architect (L1 Ex 4-6)...")
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "L1_data", "ex4_sales_status.csv"))
        # Example: Applying a conditional calculation that mimics an Excel formula
        df['Discounted_Total'] = df.apply(
            lambda row: row['Total'] * 0.85 if (row['Status'] == 'Gold' and row['Total'] > 500) else row['Total'], axis=1
        )
        print("   [Success]: Calculated Discounted_Total column using Pandas logic.")
    except FileNotFoundError:
        print("   [Skipped]: L1 data files not found. Check path/file names.")

    # --- Exercise 7-12 (Advanced Transformation) ---
    print("\n-> Running Advanced Transformations (L1 Ex 7-12)...")
    # This is where complex Pandas operations like pivot_table() would go.
    print("   [Placeholder]: Implement advanced grouping, pivoting, and aggregation logic here.")


# ==============================================================================
# LEVEL 2: SCRIPTING & AUTOMATION (Python/JS)
# Focus: Libraries for structured data processing.
# ==============================================================================
def run_l2_scripting_logic():
    """Handles exercises from L2_Scripting_Exercises.md."""
    print("\n" + "="*20 + " LEVEL 2: SCRIPTING LOGIC " + "="*20)

    # --- P1-P7 (Python Data Processing) ---
    print("-> Running Python Data Processing (L2 Ex P1-P7)...")
    try:
        # Example: Merging multiple CSVs using Pandas merge()
        df_names = pd.read_csv(os.path.join(DATA_DIR, "L2_data", "P1_employee_names.csv"))
        df_salaries = pd.read_csv(os.path.join(DATA_DIR, "L2_data", "P1_employee_salaries.csv"))
        # Merge logic here...
        print("   [Success]: Pandas merge structure defined.")
    except FileNotFoundError:
        pass

    # --- P8-P10 (Advanced Python) ---
    print("\n-> Running Advanced Python Tasks (L2 Ex P8-P10)...")
    # Placeholder for JSON loading and filtering
    print("   [Placeholder]: Implement logic to load JSON, filter by criteria, and write output.")

    # --- J1-J10 (JavaScript Logic) ---
    print("\n-> Running JavaScript Logic Simulation (L2 Ex J1-J10)...")
    # This section requires running in a JS environment (Node/Browser Console).
    print("   [Note]: These tasks are best implemented and tested directly in Node.js or the browser console.")


# ==============================================================================
# LEVEL 2.5: INTERMEDIATE AUTOMATION (PDFs & Web Scraping)
# Focus: External libraries for non-structured data.
# ==============================================================================
def run_l2_5_automation():
    """Handles exercises from L2.5_Intermediate_Exercises.md."""
    print("\n" + "="*20 + " LEVEL 2.5: INTERMEDIATE AUTOMATION " + "="*20)

    # --- PDF Tasks (P11-P14) ---
    print("-> Running PDF Mining & Manipulation (L2.5 Ex P11-P14)...")
    try:
        # Example: Using pdfplumber to extract text from a specific page range
        # with open(pdf_path, "rb") as file:
        #     with pdfplumber.open(file) as pdf:
        #         summary = pdf.pages[0].extract_text()
        print("   [Placeholder]: Implement PDF reading/extraction using pdfplumber or tabula-py.")
    except Exception as e:
        print(f"   [Skipped]: Could not run PDF tasks (Missing files/libraries). Error: {e}")

    # --- Web Scraping Tasks (W1-W4) ---
    print("\n-> Running Web Scraping & Browser Automation (L2.5 Ex W1-W4)...")
    try:
        # Example: Using Playwright to automate a browser action
        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     page = browser.new_page()
        #     page.goto("https://example.com")
        #     print(f"   [Success]: Successfully navigated to a page.")
        print("   [Placeholder]: Implement Playwright/Selenium logic here for dynamic content.")
    except Exception as e:
        print(f"   [Skipped]: Could not run web scraping tasks (Requires browser setup). Error: {e}")


# ==============================================================================
# LEVEL 3 & MASTER EXERCISES (Integration)
# Focus: Combining multiple tools and services.
# ==============================================================================
def run_master_workflows():
    """Handles Level 3 and Master exercises."""
    print("\n" + "="*20 + " LEVEL 3/MASTER: INTEGRATION WORKFLOWS " + "="*20)

    # M1-M5 are the highest level of complexity. They require all previous skills.
    print("-> Running Master Workflows (Requires L1, L2, L2.5 knowledge)...")
    print("   [Guidance]: These exercises must be built by combining functions from the modules above.")
    print("   Example: M4 requires reading a text file (L1) AND updating an SQLite DB (L3/M2).")


# ==============================================================================
# MAIN EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    setup_environment()

    print("\n\n" + "#"*70)
    print("# TO RUN THE CURRICULUM: Execute the functions in order.")
    print("# Start with L1, then move to L2, then L2.5, and finally Master Workflows.")
    print("# Remember to fill in the 'Placeholder' sections with actual code!")
    print("#"*70)

    # Run modules sequentially for guided practice
    run_l1_excel_logic()
    run_l2_scripting_logic()
    run_l2_5_automation()
    run_master_workflows()
    
    print("\n\n==============================================================")
    print("✨ ORCHESTRATION COMPLETE. Review the script and fill in the placeholders!")
    print("==============================================================")