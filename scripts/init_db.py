#!/usr/bin/env python
"""Initialize the database with updated schema"""
from app import create_app, db
import os

# Remove old database if exists
db_path = os.path.join(os.path.dirname(__file__), 'app', 'erp_system.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Removed old database at {db_path}")

app = create_app('development')

with app.app_context():
    try:
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Verify the schema was created with timetable_id
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Check attendance table columns
        attendance_columns = [col['name'] for col in inspector.get_columns('attendance')]
        if 'timetable_id' in attendance_columns:
            print("✓ Attendance table includes timetable_id column")
        else:
            print("✗ WARNING: Attendance table missing timetable_id column!")
            print(f"  Columns found: {attendance_columns}")
        
        # Check timetable table columns
        timetable_columns = [col['name'] for col in inspector.get_columns('timetable')]
        if 'course_id' in timetable_columns:
            print("✓ Timetable table includes course_id column")
        else:
            print("✗ WARNING: Timetable table missing course_id column!")
            print(f"  Columns found: {timetable_columns}")
            
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        import traceback
        traceback.print_exc()

