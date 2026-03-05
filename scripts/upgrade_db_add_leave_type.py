#!/usr/bin/env python
"""
One-time helper script to add the leave_type column to the leaves table
if it does not already exist.

Run from the project root:

    python upgrade_db_add_leave_type.py
"""

from app import create_app, db
from sqlalchemy import inspect, text


def main() -> None:
    app = create_app("development")

    with app.app_context():
        inspector = inspect(db.engine)

        # Check if leaves table exists
        tables = inspector.get_table_names()
        if "leaves" not in tables:
            print("✗ Table 'leaves' does not exist. Nothing to upgrade.")
            return

        columns = [col["name"] for col in inspector.get_columns("leaves")]

        if "leave_type" in columns:
            print("[OK] Column 'leave_type' already exists on 'leaves' table. No action needed.")
            return

        # Add the column with a sensible default
        print("Adding column 'leave_type' to 'leaves' table...")
        db.session.execute(
            text("ALTER TABLE leaves ADD COLUMN leave_type VARCHAR(50) DEFAULT 'General'")
        )
        db.session.commit()
        print("[OK] Column 'leave_type' added successfully.")


if __name__ == "__main__":
    main()

