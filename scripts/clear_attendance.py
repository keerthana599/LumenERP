"""
Clear all attendance records from the database.
Run: python clear_attendance.py
"""

from app import create_app, db
from app.models import Attendance

app = create_app('development')

with app.app_context():
    count = Attendance.query.count()
    Attendance.query.delete()
    db.session.commit()
    print(f"Attendance table reset. Removed {count} record(s).")
