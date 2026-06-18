"""
pipeline_checker.py
Runs automated data quality checks and generates a plain-English report
using Claude. Run this daily (or manually) to catch issues early.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from agent import explain_issues

DB_PATH = "nonprofit.db"


def run_checks() -> list[dict]:
    """Runs all data quality checks. Returns a list of issue dicts."""
    conn = sqlite3.connect(DB_PATH)
    issues = []

    # ── Check 1: Missing enrollment dates ────────────────────────────────────
    df = pd.read_sql("SELECT client_id, first_name, last_name FROM clients WHERE enrollment_date IS NULL OR enrollment_date = ''", conn)
    if not df.empty:
        ids = ", ".join(df["client_id"].tolist())
        issues.append({
            "type": "MISSING DATA",
            "description": f"Clients with missing enrollment dates: {ids}"
        })

    # ── Check 2: Duplicate client names ──────────────────────────────────────
    df = pd.read_sql("""
        SELECT first_name, last_name, COUNT(*) as count, GROUP_CONCAT(client_id) as ids
        FROM clients
        GROUP BY first_name, last_name
        HAVING count > 1
    """, conn)
    if not df.empty:
        for _, row in df.iterrows():
            issues.append({
                "type": "DUPLICATE",
                "description": f"'{row['first_name']} {row['last_name']}' appears {row['count']} times (IDs: {row['ids']})"
            })

    # ── Check 3: Invalid status values ───────────────────────────────────────
    valid_statuses = ("'Active'", "'Inactive'", "'Completed'", "'Pending'")
    df = pd.read_sql(f"""
        SELECT client_id, first_name, last_name, status FROM clients
        WHERE status NOT IN ({','.join(valid_statuses)})
    """, conn)
    if not df.empty:
        for _, row in df.iterrows():
            issues.append({
                "type": "INVALID STATUS",
                "description": f"Client {row['client_id']} ({row['first_name']} {row['last_name']}) has unrecognized status: '{row['status']}'"
            })

    # ── Check 4: Stale active records (no update in 30+ days) ────────────────
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    df = pd.read_sql(f"""
        SELECT client_id, first_name, last_name, last_updated
        FROM clients
        WHERE status = 'Active' AND last_updated < '{cutoff}'
    """, conn)
    if not df.empty:
        for _, row in df.iterrows():
            days_ago = (datetime.now() - datetime.strptime(row["last_updated"], "%Y-%m-%d")).days
            issues.append({
                "type": "STALE RECORD",
                "description": f"Active client {row['client_id']} ({row['first_name']} {row['last_name']}) not updated in {days_ago} days (last: {row['last_updated']})"
            })

    # ── Check 5: Appointments with no matching client ─────────────────────────
    df = pd.read_sql("""
        SELECT a.appointment_id, a.client_id, a.appointment_date
        FROM appointments a
        LEFT JOIN clients c ON a.client_id = c.client_id
        WHERE c.client_id IS NULL
    """, conn)
    if not df.empty:
        for _, row in df.iterrows():
            issues.append({
                "type": "ORPHANED RECORD",
                "description": f"Appointment {row['appointment_id']} on {row['appointment_date']} references unknown client ID: {row['client_id']}"
            })

    # ── Check 6: Clients with 3+ consecutive no-shows ────────────────────────
    df = pd.read_sql("""
        SELECT client_id, COUNT(*) as no_shows
        FROM appointments
        WHERE status = 'No-Show'
        GROUP BY client_id
        HAVING no_shows >= 3
    """, conn)
    if not df.empty:
        for _, row in df.iterrows():
            issues.append({
                "type": "AT-RISK CLIENT",
                "description": f"Client {row['client_id']} has {row['no_shows']} no-show appointments — may need outreach"
            })

    conn.close()
    return issues


def main():
    print("=" * 60)
    print(f"NONPROFIT DATA QUALITY CHECK")
    print(f"Run date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 60)
    print("\nRunning checks...\n")

    issues = run_checks()

    if issues:
        print(f"Found {len(issues)} issue(s). Generating report...\n")
    else:
        print("No issues found!\n")

    report = explain_issues(issues)
    print(report)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
