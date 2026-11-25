# RandFlow: Google Drive to PostgreSQL ETL Pipeline

**A production-minded ETL pipeline that turns messy banking CSVs into clean, queryable PostgreSQL tables — with safe reruns, full audit trails, and zero manual steps.**

Built as a solo project to demonstrate end-to-end data engineering: cloud API integration, data quality engineering, dimensional modelling, and database administration on Windows.

---

## Why This Project Exists (The Business Problem)

A retail bank exported three CSV files to Google Drive every day: customers (152 rows), accounts (221 rows), and transactions (2,025 rows). The files were deliberately messy — duplicates, inconsistent casing, impossible dates (31/02/2026), missing values, and deposits recorded with negative signs.

Analysts cleaned them by hand in Excel. The result: hours of wasted time, reports that disagreed with each other, duplicate records on reruns, and no way to trace where a number came from.

**My job was to replace that manual process with one command that runs the same way every time.**

---

## What I Built (The Solution)

A five-module Python pipeline that runs end-to-end with `python src/main.py`:

Google Drive (CSVs) → Extract (Drive API + service account) → Transform (pandas) → Load (SQLAlchemy) → PostgreSQL (staging schema) → Verify (SQL in pgAdmin)
text


**What it delivers:**

| Capability | How I implemented it |
|---|---|
| **Automated extraction** | Google Drive API with a service account (robot identity), scoped to `drive.readonly` — least privilege |
| **Consistent cleaning** | pandas: column normalisation, deduplication, date coercion with `errors='coerce'`, sign correction, title-casing |
| **Analytics-ready output** | Derived `signed_amount` column (money out = negative) so `SUM(signed_amount)` gives net position without `CASE` statements |
| **Safe reruns** | Idempotent load: deletes only the current file's old rows before inserting new ones — no duplicates, ever |
| **Full audit trail** | `source_file` and `loaded_at` on every row — every number is traceable to its origin and load time |
| **Secret hygiene** | `.env` + `.gitignore` — database passwords and API keys never touch Git |

---

## Architecture

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Google Drive │────▶│ extract.py │────▶│ transform.py │────▶│ load.py │
│ (3 CSVs) │ │ (Drive API) │ │ (pandas) │ │ (SQLAlchemy) │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
│
▼
┌──────────────┐
│ PostgreSQL │
│ (staging) │
└──────────────┘
text


**Design principle:** separation of concerns. Each module has one job. Config is centralised in `config.py`; secrets live in `.env`; the orchestrator (`main.py`) knows nothing about cleaning rules or SQL dialects.

---

## Results (First Production Run)

Found 3 file(s) in Drive folder
transactions.csv: 2025 raw rows → 1930 loaded (95 duplicates/bad rows removed)
customers.csv: 152 raw rows → 150 loaded (2 removed)
accounts.csv: 221 raw rows → 220 loaded (1 removed)
text


The gap between raw and loaded counts is the proof that the data quality rules ran. Rerunning the pipeline produces identical row counts — no duplicates.

---

## What This Project Proves I Can Do

This is the section a hiring manager should read. Each bullet maps directly to a data engineering competency.

**1. I can design an ETL pipeline end-to-end.**
I built the extract, transform, and load layers as separate, testable modules, wired them together with an orchestrator, and verified the output in the database. I understand why each layer exists and what breaks when one is skipped.

**2. I can engineer data quality, not just move data.**
The transform layer encodes business rules in code: deduplication, type coercion, sign correction, derived columns, and audit stamps. I understand that "cleaning data" means writing rules that run the same way every time — not fixing spreadsheets by hand.

**3. I understand idempotency — the difference between a script and a pipeline.**
The load step deletes only the current file's rows before inserting new ones. That single design decision is why the pipeline can be rerun safely, scheduled, or retried after a failure without corrupting the data. This is the concept most beginners miss, and it's the first thing I'd look for in a junior engineer's code.

**4. I can work with cloud APIs and secure them.**
I created a Google Cloud project, enabled the Drive API, provisioned a service account, scoped it to read-only, downloaded and protected the JSON key, and shared a Drive folder with the robot identity. I understand least privilege, why service accounts beat OAuth for unattended jobs, and why secrets never belong in source control.

**5. I can administer a PostgreSQL database.**
I installed PostgreSQL 19, created a non-superuser role, created a database owned by that role, diagnosed a PATH problem that hid `psql`, and recovered a lost superuser password via `pg_hba.conf`. I'm comfortable with schemas, roles, ownership, and the `psql` CLI.

**6. I can write SQL that answers business questions.**
The verification queries aren't `SELECT *` — they aggregate, filter, and join three tables across foreign keys to answer real questions: net spend by category, transactions per customer segment. I understand `GROUP BY`, `JOIN ... ON`, and why a derived `signed_amount` column makes financial aggregation trivial.

**7. I can debug across the whole stack.**
This project was built on Windows against a Linux-oriented runbook. I translated every command, found `psql.exe` buried in a non-standard `bin\bin` folder, recovered a forgotten password, and caught two stray-character typos by verifying each module in isolation. I don't just follow tutorials — I diagnose and fix when reality diverges from the instructions.

**8. I document and version my work.**
The repo has a `.gitignore` that excludes secrets, venv, and data. Commits are scoped and described. This README exists because a pipeline nobody can run is a pipeline nobody can trust.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Ingestion | Python 3, Google Drive API, service account |
| Transformation | pandas |
| Loading | SQLAlchemy, psycopg2 |
| Storage | PostgreSQL 19 |
| Environment | VS Code, Windows PowerShell, venv |
| Verification | SQL, pgAdmin |

---

## Quickstart (Run It Yourself)

1. Clone:
   ```bash
   git clone https://github.com/victorusman245/randflow-etl-pipeline.git
   cd randflow-etl-pipeline

    Create and activate a virtual environment, install dependencies:
    bash

    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt

    Create a .env file:
    text

    DRIVE_FOLDER_ID=your-folder-id
    SERVICE_ACCOUNT_FILE=credentials/your-key.json
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=finance_db
    DB_USER=pipeline_user
    DB_PASSWORD=your-password

    Create the database and user:
    sql

    CREATE USER pipeline_user WITH PASSWORD 'your-password';
    CREATE DATABASE finance_db OWNER pipeline_user;

    Put your Google service account JSON in credentials/ and share your Drive folder with the service account email (Viewer).

    Run:
    bash

    python src/main.py

Key Technical Decisions (And Why)
Decision	Rationale
Service account, not OAuth	The pipeline runs unattended. OAuth needs a human to click "Allow". A service account authenticates without a browser.
signed_amount as a derived column	Financial aggregation (SUM(signed_amount)) becomes a one-liner instead of a CASE expression repeated in every query. Business logic is encoded once, in the transform layer.
Delete-then-insert on load	Idempotency. The pipeline can be rerun, retried, or scheduled without producing duplicates.
Audit columns on every row	source_file and loaded_at make every number traceable. When two reports disagree, you can prove which file and which load produced each figure.
.env + .gitignore	Secrets never touch version control. A leaked database password or API key is a security incident, not a bug.
Module-per-stage design	Testable, replaceable, and readable. I can verify each module in isolation (which is how I caught two typos before they reached a full run).
SQL Verification

Row counts:
sql

SELECT COUNT(*) FROM staging.transactions;

Net spend by category (completed transactions only):
sql

SELECT category, COUNT(*) AS txns,
       ROUND(SUM(signed_amount)::numeric, 2) AS net_amount
FROM staging.transactions
WHERE status = 'Completed'
GROUP BY category
ORDER BY net_amount;

Transactions per customer segment (three-table join):
sql

SELECT c.customer_segment, COUNT(*) AS txns
FROM staging.transactions t
JOIN staging.accounts a ON a.account_id = t.account_id
JOIN staging.customers c ON c.customer_id = a.customer_id
GROUP BY c.customer_segment
ORDER BY txns DESC;

This project is the clearest evidence of what I can do as a data engineer. It demonstrates that I can:

- **Design and build an ETL pipeline end-to-end** — extract, transform, and load, as separate testable modules, wired together with an orchestrator.
- **Engineer data quality** — encode business rules in code so cleaning runs the same way every time, with audit columns on every row.
- **Secure cloud credentials** — provision a Google Cloud service account, scope it to least privilege, and keep secrets out of version control.
- **Administer a PostgreSQL database** — create roles and databases, manage schemas, and recover from environment issues (PATH, authentication) without breaking stride.
- **Write analytical SQL** — aggregate, filter, and join three tables across foreign keys to answer real business questions.
- **Debug across the whole stack** — when the runbook said one thing and the machine did another, I diagnosed and fixed it.

I didn't follow a tutorial. I adapted one, hit real problems, and solved them. That's what this repo shows.