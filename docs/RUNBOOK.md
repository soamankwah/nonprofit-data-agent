# 📖 Runbook — Nonprofit Data Assistant

**For:** Program coordinators and data staff who maintain this tool after handoff
**Reading time:** 10 minutes

---

## What This Tool Does

This tool has two parts:

1. **Daily Pipeline Check** — automatically scans your database for data problems (missing records, duplicates, stale entries) and explains them in plain English
2. **Chat Interface** — lets you ask questions about your program data without knowing SQL

---

## Running the Daily Check

Open your terminal and run:

```bash
python src/pipeline_checker.py
```

You'll see a report like this:

```
Found 3 issues. Generating report...

DATA QUALITY REPORT — June 17, 2026

1. MISSING DATA: Clients C-0023 and C-0041 are missing enrollment dates...
   → Action: Ask the intake team to complete these records.

2. DUPLICATE: "Maria Johnson" appears twice...
```

**When to run it:** Every Monday morning, or after any bulk data import.

---

## Using the Chat Interface

Start the app:
```bash
streamlit run src/app.py
```

Then open `http://localhost:8501` in your browser.

Type your question in the chat box. Examples:
- "Which clients haven't had an appointment in 30 days?"
- "How many clients is Maria Torres managing right now?"
- "Show me all Pending clients"

---

## Adding New Data

1. Update the CSV files in the `data/` folder
2. Re-run `python src/load_data.py` to refresh the database
3. The chat and checker will automatically use the new data

---

## Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| "API key not found" error | Check that your `.env` file has `ANTHROPIC_API_KEY=...` |
| "Database not found" error | Run `python src/load_data.py` first |
| App won't start | Make sure you ran `pip install -r requirements.txt` |
| Wrong answers from Claude | The data in your CSVs may be outdated — re-run load_data.py |

---

## Who to Call

- **Technical issues:** Contact the original builder (Samuel Amankwah — samuelamankwah145@gmail.com)
- **Anthropic API key:** Your organization's IT administrator
- **Data questions:** Your program director

---

## Updating the API Key

1. Open the `.env` file in the project folder
2. Replace the value after `ANTHROPIC_API_KEY=`
3. Save the file — no restart needed

---

*Last updated: June 2026 | Built by Samuel Amankwah*
