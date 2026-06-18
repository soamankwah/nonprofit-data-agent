"""
load_data.py
Loads CSV files into a local SQLite database.
Run this once before using the agent or pipeline checker.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "nonprofit.db"

def load_data():
    print("Loading data into SQLite database...")
    conn = sqlite3.connect(DB_PATH)

    # Load clients
    clients = pd.read_csv("data/clients.csv")
    clients.to_sql("clients", conn, if_exists="replace", index=False)
    print(f"  ✅ Loaded {len(clients)} client records")

    # Load appointments
    appointments = pd.read_csv("data/appointments.csv")
    appointments.to_sql("appointments", conn, if_exists="replace", index=False)
    print(f"  ✅ Loaded {len(appointments)} appointment records")

    conn.close()
    print(f"\nDatabase saved to: {DB_PATH}")
    print("You can now run: python src/pipeline_checker.py")

if __name__ == "__main__":
    load_data()
