"""
One-time script to remove all timetable (schedule) entries from the database.
Run this to clear dummy/seed timetable data so the Manage Timetable page shows no entries.

Usage: python clear_timetable_data.py
"""

from app import create_app, db
from app.models import Timetable, Attendance

app = create_app('development')

with app.app_context():
    # Unlink attendance records that reference a timetable
    updated = Attendance.query.filter(Attendance.timetable_id.isnot(None)).update({Attendance.timetable_id: None})
    if updated:
        db.session.commit()
        print(f"Unlinked {updated} attendance record(s) from timetable.")
    count = Timetable.query.count()
    Timetable.query.delete()
    db.session.commit()
    print(f"Removed {count} timetable slot(s). Manage Timetable will now show no entries until you add new ones.")
