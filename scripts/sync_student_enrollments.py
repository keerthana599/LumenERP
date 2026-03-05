"""
Sync student-course enrollments so Mark Attendance and other features get data.

For each student, creates Enrollment records for every course that matches
their department and semester (so students are "in" the classes for their class).
Existing enrollments are left as-is (no duplicates; unique on student_id + course_id).

Run once to backfill: python sync_student_enrollments.py
Or use Admin → Students → "Sync enrollments" in the app.
"""

from app import create_app, db
from app.models import Student, Course, Enrollment

app = create_app('development')

with app.app_context():
    added = 0
    students = Student.query.all()
    for student in students:
        # All courses in same department and semester as this student
        courses = Course.query.filter_by(
            department_id=student.department_id,
            semester=student.semester
        ).all()
        for course in courses:
            existing = Enrollment.query.filter_by(
                student_id=student.id,
                course_id=course.id
            ).first()
            if not existing:
                en = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    status='enrolled'
                )
                db.session.add(en)
                added += 1
    db.session.commit()
    print(f"Enrollments synced. Added {added} new enrollment(s). Students are now linked to courses by department and semester.")
