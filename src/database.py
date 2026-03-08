import sqlite3
import pandas as pd
import os

DB_PATH = "data/yield_engine.db"

def init_db():
    """Initializes the database and creates the evaluations table."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            candidate_name TEXT,
            match_score INTEGER,
            matched_skills TEXT,
            missing_skills TEXT,
            experience_years INTEGER,
            core_skills TEXT,
            tools TEXT,
            projects TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_evaluation(data_list):
    """Saves multiple evaluation records into the database."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame(data_list)
    # Append the new data to the existing table
    df.to_sql("evaluations", conn, if_exists="append", index=False)
    conn.close()

def get_all_evaluations():
    """Retrieves all history from the database."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM evaluations ORDER BY timestamp DESC", conn)
    conn.close()
    return df