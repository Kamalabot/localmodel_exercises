# Level 3: Master Level - Integration & Visualization

## Phase 1: The Master Toolset

### 1. Database Engine
*   We will use **SQLite** (built-in to Python) for local data persistence.
*   Tool: `sqlite3` in Python or a VS Code SQLite Viewer extension.

### 2. Motion Graphics (GSAP)
*   **GSAP (GreenSock Animation Platform)** is the industry standard for high-performance web animations.
*   Installation: CDN or `npm install gsap`.

### 3. API & Web Frameworks
*   Use `requests` for API simulation in Python.
*   Optional: Use **Vite** or a simple HTML/JS setup for visualizations.

---

## Phase 2: Master Exercises

### Exercise M1: Automated Weather Sentiment Tracker
*   **Goal:** Fetch weather data (simulated) and determine if it's "Outdoor Friendly".
*   **Task:** 
    1. Write a Python script to read a list of cities.
    2. Simulate an API call to get Temperature and Condition.
    3. Determine "Sentiment" (e.g., Sunny + 75F = "Perfect").
    4. Generate a JSON file for the UI.

### Exercise M2: SQLite CRM with Natural Language Querying
*   **Goal:** Build a database and "talk" to it.
*   **Task:**
    1. Write a script to convert `exercise_data/L1_data/ex7_team_names.csv` and `exercise_data/L2_data/P1_employee_salaries.csv` into an SQLite database.
    2. Create a "Query Agent" function that takes a string like "Show me all Engineering leads" and generates/executes the correct SQL.

### Exercise M3: Interactive Financial GSAP Visualization
*   **Goal:** Animate data trends.
*   **Task:**
    1. Create a web page that loads `exercise_data/L1_data/ex10_11_12_sales_master.csv`.
    2. Use **GSAP** to create a "Bar Chart" where the bars grow from 0 to their value on load.
    3. Add a "Stagger" animation to the labels.

### Exercise M4: The "Context-Aware" Data Pipeline
*   **Goal:** Cross-document intelligence.
*   **Task:**
    1. Read `exercise_data/L1_data/ex15_project_reference.txt`.
    2. Extract the mapping of Project Name -> Cost Center.
    3. Automatically update an SQLite table of projects with these IDs.
    4. Log the "Success" or "Not Found" status for each entry.

### Exercise M5: AI-Powered Portfolio Generator
*   **Goal:** Turn messy data into a premium UI.
*   **Task:**
    1. Take the messy text from `exercise_data/L1_data/ex1_messy_profile.txt`.
    2. Use a script to parse the Name, Role, and Skills.
    3. Generate an HTML `index.html` that uses **GSAP** for a high-end "Reveal" animation of the portfolio sections.
