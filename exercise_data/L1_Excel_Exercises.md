# Level 1: Excel & Pi for Excel Exercises

## Phase 1: The Setup (15 Minutes)

### 1. LM Studio (The Engine)
* **Goal:** Run a powerful reasoning model locally to keep your data private.
* **Action:** 
    1. Open **LM Studio**.
    2. Search for and download a model like `DeepSeek-V3` or `Qwen-2.5-Coder-7B-Instruct`.
    3. Go to the **AI Chat** tab, load the model, and ensure the "Server" is running if using external plugins.

### 2. Pi for Excel (The Interface)
* **Goal:** Use AI directly inside your spreadsheets.
* **Action:**
    1. Search for "Pi for Excel" on GitHub or your organization's add-in store.
    2. Install the add-in.
    3. Open Excel; you should see a "Pi" icon in the Ribbon or a sidebar.
    4. Connect Pi to your local LM Studio server (usually `http://localhost:1234/v1`).

---

## Phase 2: The Exercises (60 Minutes)

### I. The "Data Scavenger"
* **Exercise 1: Clean Copy-Paste**
    * **File:** `ex1_messy_profile.txt`
    * **Prompt:** *"Extract the Name, Email, and Company into separate columns."*
* **Exercise 2: Browser-to-Sheet**
    * **File:** `ex2_clipboard_table.txt`
    * **Prompt:** *"Read my clipboard and format it as a clean Excel table with proper headers."*
* **Exercise 3: The "Note" Gatherer**
    * **File:** `ex3_unstructured_notes.txt`
    * **Prompt:** *"Take these unstructured notes and create a task list in a new sheet with Status and Priority columns."*

### II. The "Formula Architect"
* **Exercise 4: Natural Language Formulas**
    * **File:** `ex4_sales_status.csv`
    * **Prompt:** *"Write a formula that calculates a 15% discount but only if the 'Status' is 'Gold' and the 'Total' is over $500."*
* **Exercise 5: Regex for Humans**
    * **File:** `ex5_messy_phones.csv`
    * **Prompt:** *"Clean this column of phone numbers so they all follow the format (XXX) XXX-XXXX."*
* **Exercise 6: Error Hunter**
    * **File:** `ex6_broken_formulas.csv`
    * **Prompt:** *"Identify why these formulas are breaking and fix them."*

### III. Data Transformation
* **Exercise 7: The Complex Transposer (Advanced)**
    * **File:** `ex7_team_names.csv` (Contains Name, Dept, Role, Allocation)
    * **Prompt:** *"Turn this list into a matrix where Departments are rows, Project Roles are columns, and the cells show the sum of Allocation %."*
* **Exercise 8: Logic Deduplication (Advanced)**
    * **File:** `ex8_user_logs.csv` (Contains overlapping User IDs, Dates, and Statuses)
    * **Prompt:** *"Find duplicates in User ID. For each duplicate, keep the row with the most recent 'Last Login'. If the dates are the same, prioritize rows where Status is 'Active'."*
* **Exercise 9: Category Creator**
    * **File:** `ex9_transactions.csv`
    * **Prompt:** *"Look at these transaction descriptions and create a new 'Category' column (e.g., Food, Transport, Utilities) automatically."*

### IV. "Logic Distiller"
* **Exercise 10: Summary Generator**
    * **File:** `ex10_11_12_sales_master.csv` (100 rows)
    * **Prompt:** *"Give me a 3-bullet point executive summary of the trends you see here regarding product performance and regional growth."*
* **Exercise 11: The "What-If" Machine**
    * **File:** `ex10_11_12_sales_master.csv`
    * **Prompt:** *"If I increase the 'Price' by 5% and 'Costs' stay the same, show me the projected 'Profit' in a new column. Name the column 'Adjusted Profit'."*
* **Exercise 12: Pivot Table Planner**
    * **File:** `ex10_11_12_sales_master.csv`
    * **Prompt:** *"How should I structure a Pivot Table to see total sales by Region and Month? Give me the exact fields for Rows, Columns, and Values."*

### V. Advanced Automation
* **Exercise 13: Bulk Email Drafter**
    * **File:** `ex13_billing.csv`
    * **Prompt:** *"Based on the names in Column A and the 'Amount Due' in Column B, write a polite follow-up email draft for each row. Mention the 'Account Status' and the 'Due Date'."*
* **Exercise 14: Data Validation**
    * **File:** `ex14_validation_source.csv`
    * **Prompt:** *"Create a data validation list for Column C based on the unique project names found in Column F."*
* **Exercise 15: The "Context Bridge"**
    * **File:** `ex15_project_reference.txt` (External Doc)
    * **Task:** Open both your Excel sheet (use `ex10_11_12_sales_master.csv` and add a 'Project Name' column if missing) and this text file.
    * **Prompt:** *"Read the provided memorandum and fill in the missing 'Cost Center' IDs in my spreadsheet based on the project names you find."*
