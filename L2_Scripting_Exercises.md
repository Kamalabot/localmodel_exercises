# Level 2: Advanced Scripting & Automation (Python & JS)

## Phase 1: The Environment Setup

### 1. Python Environment
*   Ensure you have **Python 3.10+** installed.
*   Install necessary libraries:
    ```bash
    pip install pandas matplotlib textblob openpyxl
    ```

### 2. JavaScript Environment
*   Run snippets in the **Browser Console (F12)** or **Node.js**.

---

## Phase 2: Python Exercises (Data & Automation)

1.  **Exercise P1: The Multi-Source Merger**
    *   **Files:** `exercise_data/L2_data/P1_employee_names.csv`, `exercise_data/L2_data/P1_employee_salaries.csv`, `exercise_data/L2_data/P1_employee_locations.csv`
    *   **Task:** Merge files into `master_report.csv`. Fill missing data with "DATA MISSING".

2.  **Exercise P2: Automated Sentiment Scoring**
    *   **File:** `exercise_data/L2_data/P2_customer_reviews.csv`
    *   **Task:** Add a `Sentiment_Score` column based on keywords or libraries.

3.  **Exercise P3: Executive Chart Generator**
    *   **File:** `exercise_data/L2_data/P3_performance_data.csv`
    *   **Task:** Create a dual-axis chart (Sales vs Leads) using `matplotlib`.

4.  **Exercise P4: Log File Parser**
    *   **File:** `exercise_data/L2_data/P4_server_logs.txt`
    *   **Task:** Extract all lines containing `[ERROR]` and count them. Output a summary text.

5.  **Exercise P5: CSV to JSON Converter**
    *   **File:** `exercise_data/L2_data/P3_performance_data.csv`
    *   **Task:** Convert the CSV into a JSON array of objects.

6.  **Exercise P6: Bulk Filename Sanitizer**
    *   **Task:** Write a script that takes a list of strings (filenames like `Report 2024 (v1).pdf`) and cleans them to `report_2024_v1.pdf` (lowercase, no spaces, no special chars).

7.  **Exercise P7: Password Security Auditor**
    *   **File:** `exercise_data/L2_data/P7_passwords.txt`
    *   **Task:** Check each password. Rule: Min 8 chars, 1 number, 1 special char. Output a list of "Weak" vs "Strong" passwords.

8.  **Exercise P8: API Data Filtering (Mock)**
    *   **File:** `exercise_data/L2_data/J2_user_profiles.json`
    *   **Task:** Load the JSON and filter for users who have the "Job Title" containing "CEO".

9.  **Exercise P9: Inventory Reorder Logic**
    *   **File:** `exercise_data/L2_data/P9_inventory.csv`
    *   **Task:** Identify items where `CurrentStock` is less than `MinStock`. Generate a `reorder_list.csv` with the ItemID and the amount to buy to reach `MinStock + 10`.

10. **Exercise P10: Directory Tree Walker**
    *   **Task:** Write a script using `os.walk` to list all files in the `exercise_data` folder and save the output to `workspace_structure.txt`.

---

## Phase 3: JavaScript Exercises (Logic & Web)

1.  **Exercise J1: The Live Dashboard Parser**
    *   **File:** `exercise_data/L2_data/J1_dashboard_stats.json`
    *   **Task:** Calculate the **Average Revenue per Visitor** from the `daily_stats` array.

2.  **Exercise J2: Browser Form Auto-Filler**
    *   **File:** `exercise_data/L2_data/J2_user_profiles.json`
    *   **Task:** Iterate through the JSON and "fill" a mock form object for the user named "Clark Kent".

3.  **Exercise J3: Complex Data Validator (RegEx)**
    *   **Task:** Write a function `validateSKU(sku)` for pattern: `SKU-DDDD-UU` (D=digit, U=Uppercase).

4.  **Exercise J4: Real-time Currency Converter**
    *   **File:** `exercise_data/L2_data/J4_exchange_rates.json`
    *   **Task:** Create a function `convertToEUR(usdAmount)` using the rates in the JSON file.

5.  **Exercise J5: Array Deduplicator & Sorter**
    *   **Task:** Take an array of objects `[{id:1, name:'B'}, {id:2, name:'A'}, {id:1, name:'B'}]` and return a unique array sorted by name.

6.  **Exercise J6: Countdown Timer Logic**
    *   **Task:** Create a function that takes a target date and returns a string: "X days, Y hours remaining".

7.  **Exercise J7: URL Parameter Extractor**
    *   **File:** `exercise_data/L2_data/J7_urls.txt`
    *   **Task:** Take a URL from the list and return a JS object of its query parameters (e.g., `{q: "ai coding", limit: "10"}`).

8.  **Exercise J8: HTML List Generator**
    *   **Task:** Take an array `['Home', 'About', 'Contact']` and return the string `<ul><li>Home</li><li>About</li><li>Contact</li></ul>`.

9.  **Exercise J9: Debounce Implementation**
    *   **Task:** Write a `debounce(func, delay)` function to limit how often a function can be called.

10. **Exercise J10: Deep Object Searcher**
    *   **File:** `exercise_data/L2_data/J10_nested_config.json`
    *   **Task:** Write a function `getNestedValue(obj, path)` where path is a string like `"app.settings.network.security.apiKey"`.
