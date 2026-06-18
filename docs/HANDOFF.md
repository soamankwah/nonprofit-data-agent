# 🤝 Handoff Guide — Nonprofit Data Assistant

**For:** The person taking ownership of this tool after the original builder leaves

---

## Before the Builder Leaves — Checklist

- [ ] You can run `python src/pipeline_checker.py` successfully on your own machine
- [ ] You can launch `streamlit run src/app.py` and ask it a question
- [ ] You have your own copy of the `.env` file with the API key
- [ ] You know where the CSV data files live and how to update them
- [ ] You've read the RUNBOOK.md
- [ ] You've broken something on purpose and fixed it (with help)
- [ ] You know who to call for technical help

---

## What You Own Now

| File/Folder | What It Does | How Often You Touch It |
|-------------|--------------|------------------------|
| `data/*.csv` | Your program data | When data changes |
| `src/pipeline_checker.py` | The automated checks | Rarely — only if checks need updating |
| `src/app.py` | The chat interface | Rarely |
| `.env` | API key | When key expires/changes |
| `docs/RUNBOOK.md` | Your day-to-day guide | Read it |

---

## The One Thing That Breaks Most Often

**The database gets out of sync with your CSV files.**

If Claude is giving you old or wrong answers, run:
```bash
python src/load_data.py
```

This refreshes the database from your CSV files. Do this any time you update the data.

---

## Adding a New Data Check

If you want to check for a new type of problem (e.g. "flag clients who haven't had an outcome recorded"), open `src/pipeline_checker.py` and add a new block following the same pattern as the existing checks. Each check:
1. Runs a database query
2. Adds an issue dict to the `issues` list if something is wrong

Claude handles the explanation automatically.

---

## If You Get Stuck

1. Check the RUNBOOK.md first
2. Google the exact error message
3. Email Samuel Amankwah (samuelamankwah145@gmail.com) — happy to help even after the fellowship

---

*This document exists because good tools outlast their builders.*
*— Samuel Amankwah, June 2026*
