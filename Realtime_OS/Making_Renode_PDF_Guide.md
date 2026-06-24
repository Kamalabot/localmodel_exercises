# Renode Zephyr Simulation Setup Guide

**Exported:** 6/24/2026 13:00:51  
**Link:** [https://gemini.google.com/app/c25fd38c21f9a889](https://gemini.google.com/app/c25fd38c21f9a889)

## Response:
You are completely right, I left those critical manual steps out of the final summary. My apologies for the oversight.

Here is the complete, unbroken end-to-end roster exactly as requested, enclosed entirely in a markdown block so you can easily copy, paste, or save it as a reference gist for later automation.

```
# Windows Local Build Roster: Renode PDF Documentation

**Prerequisites:** Python, Git, and MiKTeX installed.

### Phase 1: Environment Setup & Source Generation
1. Open your native Windows Command Prompt (`cmd.exe`).
2. Clone the repository and configure the Python environment:
   ```cmd
   git clone [https://github.com/renode/renode-docs.git](https://github.com/renode/renode-docs.git)
   cd renode-docs
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
```

3.  Generate the raw LaTeX layout files using Sphinx (pointing explicitly to the `source` directory):
    ```
    python -m sphinx -M latexpdf source _build
    ```

### Phase 2: Patching the Missing Antmicro Stylesheet

The official Antmicro styling package is installed inside the Python virtual environment, but the Windows Sphinx builder fails to migrate it to the final LaTeX folder.

1.  From the root `renode-docs` directory, search for the missing file:
    ```
    dir /s /b sphinx_antmicro.sty
    ```
2.  Highlight and copy the absolute path returned by the command.
3.  Copy that file directly into your LaTeX staging folder (replace `[PASTED_PATH]` with the path you just copied):
    ```
    copy "[PASTED_PATH]" _build\latex\
    ```

### Phase 3: Patching Windows Path Crashes

Sphinx injects raw Windows backslashes (`\`) for local asset paths (like the Antmicro logo). LaTeX interprets backslashes as code commands, causing an immediate crash.

1.  Navigate into the staging folder:
    ```
    cd _build\latex
    ```
2.  Open `renode-docs.tex` in your preferred text editor.
3.  Use **Ctrl+F** to search for your root drive letter (e.g., `D:`).
4.  Locate the `\sphinxlogo` macro line (e.g., `\sphinxlogo{D:\gitFolders\...}`).
5.  **Change all backslashes (`\`) inside that specific path to forward slashes (`/`).**
    *   _Change:_ `\sphinxlogo{D:\gitFolders\renode-docs\.venv\...}`
    *   _To:_ `\sphinxlogo{D:/gitFolders/renode-docs/.venv/...}`
6.  Save and close the file.

### Phase 4: Final PDF Compilation

Because Windows lacks the Perl script engine required by `latexmk`, you must trigger the native `pdflatex` engine directly. Running it in `nonstopmode` ensures it automatically bypasses missing decorative assets (like `latex.png`) without halting the build.

1.  **Run Pass 1** (Generates layout, installs missing MiKTeX packages, leaves references broken):
    ```
    pdflatex -interaction=nonstopmode renode-docs.tex
    ```
    _(Note: When the MiKTeX dialog box pops up to install layout packages, uncheck "Ask me next time" and click **Install**)._
2.  **Run Pass 2** (Maps the Table of Contents and fixes hyper-references):
    ```
    pdflatex -interaction=nonstopmode renode-docs.tex
    ```

**Success:** Your fully compiled, standalone manual is now generated at: `_build\latex\renode-docs.pdf`



---
Powered by [Gemini Exporter](https://www.ai-chat-exporter.com)