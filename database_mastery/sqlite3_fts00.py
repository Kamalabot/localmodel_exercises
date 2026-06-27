import sqlite3

def run_fts_sandbox():
    print("Initializing FTS5 Local Sandbox...\n")
    
    # 1. Initialize local in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Ensure rows are returned as dictionaries for cleaner output
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 2. Create the FTS5 Virtual Table
    # The 'porter' tokenizer stems words, so searching "run" will match "running"
    # The 'unicode61' tokenizer normalizes characters (e.g., stripping accents)
    cursor.execute("""
        CREATE VIRTUAL TABLE library USING fts5(
            title, 
            content, 
            tokenize='porter unicode61'
        );
    """)

    # 3. Insert sample data
    documents = [
        ("The AI Revolution", "Agents are using local LLMs to manage states."),
        ("Local First Engineering", "Sovereign compute means owning your data and your hardware."),
        ("SQLite Masterclass", "FTS5 allows for blazing fast text search without heavy vector databases."),
        ("Performance Metrics", "A standard laptop can easily run an SQLite FTS5 index for millions of rows.")
    ]
    
    cursor.executemany("INSERT INTO library (title, content) VALUES (?, ?)", documents)
    conn.commit()

    # 4. Exact Keyword Match
    print("--- Exact Match Search ('SQLite') ---")
    cursor.execute("SELECT title FROM library WHERE library MATCH 'SQLite'")
    for row in cursor.fetchall():
        print(f"Match: {row['title']}")

    # 5. Boolean Search (AND / OR / NOT)
    print("\n--- Boolean Search ('local AND data') ---")
    cursor.execute("SELECT title FROM library WHERE library MATCH 'local AND data'")
    for row in cursor.fetchall():
        print(f"Match: {row['title']}")

    # 6. Ranked Search with BM25 and Highlights
    # highlight(table_name, column_index, open_tag, close_tag)
    print("\n--- Ranked Search with Highlights ('fast OR local') ---")
    query = """
        SELECT 
            title, 
            highlight(library, 1, '>>', '<<') as highlighted_content,
            bm25(library) as score
        FROM library 
        WHERE library MATCH 'fast OR local'
        ORDER BY score ASC; 
    """
    
    # NOTE ON RANKING: 
    # SQLite's BM25 function returns negative values. The more negative the score, 
    # the better the match. Sorting ascending (ASC) brings the best results to the top.
    cursor.execute(query)
    
    for row in cursor.fetchall():
        print(f"[{row['score']:.2f}] {row['title']} | {row['highlighted_content']}")

    conn.close()

if __name__ == "__main__":
    run_fts_sandbox()