# Att_School - Attendance System

This is a simple Flask-based attendance system using SQLite. It includes:

- Admin (login/password) to import lists and export PDFs
- Staff (login/password) to view daily attendance and export Excel
- Teacher quick-login (select name & class, no password) to record attendance per period
- Excel export (per-day file updated when attendance recorded) with RTL sheets
- PDF export of daily attendance

Quick local setup

1. Create a virtualenv and install requirements (PowerShell):

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Initialize the database and create default admin:

```pwsh
flask --app app init-db
```

3. Run locally:

```pwsh
flask --app app run
```

Default admin username: `Administrator`, password: `admin` (change in production).

Deploying to Render

1. Create a Web Service on Render using this repo.
2. Set the build command: `pip install -r requirements.txt`
3. Start command is already set by `Procfile` (`gunicorn app:app`).
4. Add an environment variable `SECRET_KEY` for production.

Notes and next steps

- The import expects sheets named `classes`, `students`, `teachers`, `subjects`.
- Excel creation uses `exports/attendance-YYYY-MM-DD.xlsx` and sets each sheet to RTL.
- For robust production PDFs consider WeasyPrint (needs additional system deps).
