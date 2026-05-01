# Local Model Training: From Excel to Automation Master

Welcome to the local model training exercises. These exercises are designed to help you master AI-assisted workflows using local LLMs and coding agents.

## 🚀 Levels of Mastery

### 1. [Level 1: Excel & Pi for Excel](./L1_Excel_Exercises.md)
*   **Focus:** Direct spreadsheet interaction, natural language formulas, and data cleaning.
*   **Tools:** Excel + Pi for Excel + LM Studio.
*   **Key Files:** Located in `exercise_data/L1_data`.

---

### 2. [Level 2: Advanced Scripting & Automation](./L2_Scripting_Exercises.md)
*   **Focus:** Data engineering, automated reporting, and web automation logic.
*   **Tools:** Python (Pandas/Matplotlib), JavaScript, Coding Agents.
*   **Key Files:** Located in `exercise_data/L2_data`.

---

### 2.5 [Level 2.5: Intermediate Automation (PDFs & Web Scraping)](./L2.5_Intermediate_Exercises.md)
*   **Focus:** Document data extraction (PDFs), Web Scraping basics, and Browser Automation.
*   **Tools:** PyPDF2, BeautifulSoup, Playwright.
*   **Key Files:** Located in `exercise_data/L2.5_data`.

---

### ACP Configs
The following configuration details are for agent servers:
```json
  "agent_servers": {
    "pi-acp":
    { "type": "registry" },
      "pi-windows": {
        "type": "custom",
        "command": "npx.cmd",
        "args": ["-y", "pi-acp"],
        "env": {
          "PATH": "C:\\Program Files\\nodejs;C:\\Windows\\system32"
      }
    }
```
---

## 🛠️ Global Prerequisites
1.  **LM Studio:** For running local inference.
2.  **Coding Agent:** (e.g., Antigravity, Cline, or VS Code Copilot) to assist with script writing in Level 2 & 3.
3.  **Exercise Data:** All raw materials are organized in their respective level folders.
