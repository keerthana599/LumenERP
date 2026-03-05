# Project Structure

This document describes the organized structure of the LumenERP project.

## Directory Layout

```
LumenERP/
├── app/                          # Flask application core
│   ├── __init__.py              # Flask app initialization
│   ├── config.py                # Configuration settings
│   ├── constants.py             # Application constants
│   ├── models.py                # Database models
│   ├── admin/                   # Admin module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/                    # Authentication module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── faculty/                 # Faculty module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/                    # Main routes module
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── student/                 # Student module
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── file_handler.py
│
├── static/                      # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/                 # User uploads
│       ├── certificates/
│       └── notes/
│
├── templates/                   # HTML templates
│   ├── base.html
│   ├── base_student_portal.html
│   ├── base_portal.html
│   ├── admin/                   # Admin templates
│   ├── auth/                    # Authentication templates
│   ├── attendance/              # Attendance templates
│   ├── certificates/            # Certificate templates
│   ├── dashboard/               # Dashboard templates
│   ├── fees/                    # Fee templates
│   ├── leave/                   # Leave templates
│   ├── main/                    # Main templates
│   ├── notes/                   # Notes templates
│   ├── partials/                # Partial/component templates
│   ├── staff/                   # Staff templates
│   └── timetable/               # Timetable templates
│
├── scripts/                     # Utility scripts
│   ├── clear_attendance.py      # Clear attendance records
│   ├── clear_timetable_data.py  # Clear timetable data
│   ├── create_admin.py          # Create admin user
│   ├── init_db.py               # Initialize database
│   ├── seed_data.py             # Seed sample data
│   ├── sync_student_enrollments.py
│   └── upgrade_db_add_leave_type.py
│
├── docs/                        # Documentation
│   ├── DEVELOPMENT_GUIDE.md     # Development guidelines
│   ├── GETTING_STARTED.md       # Quick start guide
│   └── IMPLEMENTATION_SUMMARY.md # Implementation details
│
├── data/                        # Data files
│   └── erp_system.db            # SQLite database
│
├── UI-screenshots/              # UI screenshots/mockups
│
├── .git/                        # Git repository
├── .venv/                       # Virtual environment (in .gitignore)
├── .vscode/                     # VSCode settings
├── .gitignore                   # Git ignore rules
├── README.md                    # Project readme
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

## Key Changes Made

1. **Created `/scripts/` folder** - All database and utility scripts moved here:
   - `clear_attendance.py`
   - `clear_timetable_data.py`
   - `create_admin.py`
   - `init_db.py`
   - `seed_data.py`
   - `sync_student_enrollments.py`
   - `upgrade_db_add_leave_type.py`

2. **Created `/docs/` folder** - All documentation moved here:
   - `DEVELOPMENT_GUIDE.md`
   - `GETTING_STARTED.md`
   - `IMPLEMENTATION_SUMMARY.md`

3. **Created `/data/` folder** - Database storage location:
   - `erp_system.db` moved here

4. **Cleaned up** - Removed all `__pycache__/` directories throughout the project

5. **Updated Configuration** - Modified `app/config.py` to reference the new database location

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## Using Utility Scripts

Scripts are now located in the `scripts/` folder:

```bash
# Initialize database
python scripts/init_db.py

# Create admin user
python scripts/create_admin.py

# Seed sample data
python scripts/seed_data.py
```

## Notes

- The `.venv/` folder is in `.gitignore` and should not be committed
- The `data/` folder can be added to `.gitignore` if you don't want to commit the database
- All __pycache__ directories are auto-generated and should stay in `.gitignore`
