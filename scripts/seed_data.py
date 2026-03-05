"""
Sample Data Seeder for College ERP System
Run this script to populate the database with sample data for testing
"""

from app import create_app, db
from app.models import (
    User, Student, Faculty, Attendance, Leave, Fee, Note, 
    Certificate, Staff, Department, Course
)
from datetime import datetime, timedelta
import random

app = create_app('development')

def seed_database():
    """Populate database with sample data"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Clear existing data (optional)
        # db.drop_all()
        # db.create_all()
        
        # Add sample departments first
        print("Adding departments...")
        dept_list = [
            {'name': 'Computer Science', 'code': 'CS'},
            {'name': 'Electronics', 'code': 'EC'},
            {'name': 'Mechanical', 'code': 'ME'},
            {'name': 'Civil', 'code': 'CE'},
            {'name': 'Information Technology', 'code': 'IT'},
        ]
        
        departments_map = {}
        for dept_data in dept_list:
            dept = Department.query.filter_by(code=dept_data['code']).first()
            if not dept:
                dept = Department(
                    name=dept_data['name'],
                    code=dept_data['code'],
                    head='Prof. ' + dept_data['name'].split()[0]
                )
                db.session.add(dept)
                db.session.commit()
            departments_map[dept_data['name']] = dept.id
        
        # Add sample students
        print("Adding students...")
        students_data = [
            ('CS2024001', 'Alice Kumar', 'Computer Science'),
            ('CS2024002', 'Bob Singh', 'Computer Science'),
            ('CS2024003', 'Carol Sharma', 'Computer Science'),
            ('EC2024001', 'David Patel', 'Electronics'),
            ('EC2024002', 'Emma Wilson', 'Electronics'),
        ]
        
        for roll_no, name, dept_name in students_data:
            # Check if student already exists
            if Student.query.filter_by(roll_no=roll_no).first():
                print(f"  Student {roll_no} already exists, skipping...")
                continue
                
            user = User(
                username=name.lower().replace(' ', '_'),
                email=f"{name.lower().replace(' ', '.')}@student.edu",
                role='student',
                is_active=True
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            student = Student(
                user_id=user.id,
                roll_no=roll_no,
                department_id=departments_map[dept_name],
                semester=random.randint(1, 8),
                phone=f'98{random.randint(10000000, 99999999)}'
            )
            db.session.add(student)
        
        db.session.commit()
        
        # Add attendance records
        print("Adding attendance records...")
        students = Student.query.all()
        for student in students:
            for i in range(30):
                date = datetime.utcnow().date() - timedelta(days=i)
                status = random.choice(['present', 'absent', 'leave'])
                
                # Check if record exists (using all columns due to unique constraint)
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    timetable_id=None,
                    date=date
                ).first()
                
                if not existing:
                    attendance = Attendance(
                        student_id=student.id,
                        timetable_id=None,
                        date=date,
                        status=status,
                        marked_by='faculty'
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        
        # Add fees
        print("Adding fee records...")
        for student in students:
            for sem in range(1, 9):
                fee = Fee(
                    student_id=student.id,
                    semester=sem,
                    amount=50000 + random.randint(0, 10000),
                    status=random.choice(['paid', 'pending']),
                    paid_date=datetime.utcnow() if random.choice([True, False]) else None,
                    due_date=datetime.utcnow().date() + timedelta(days=random.randint(1, 60))
                )
                try:
                    db.session.add(fee)
                except:
                    db.session.rollback()
        
        db.session.commit()
        
        # Add sample staff
        print("Adding staff...")
        designations = ['Registrar', 'Finance Officer', 'Librarian', 'Director', 'HOD']
        staff_dept_codes = ['CS', 'EC', 'ME', 'CE', 'IT']
        
        for i in range(5):
            # Get department by code
            dept = Department.query.filter_by(code=staff_dept_codes[i]).first()
            if dept:
                staff = Staff(
                    name=f'Staff Member {i+1}',
                    designation=designations[i],
                    department_id=dept.id,
                    email=f'staff{i+1}@college.edu',
                    phone=f'98{random.randint(10000000, 99999999)}',
                    office=f'Block A, Room {101 + i}'
                )
                db.session.add(staff)
        
        db.session.commit()
        
        print("Database seeding completed successfully!")
        print("\nSummary:")
        print(f"  • Students: {Student.query.count()}")
        print(f"  • Faculty: {Faculty.query.count()}")
        print(f"  • Attendance Records: {Attendance.query.count()}")
        print(f"  • Fees: {Fee.query.count()}")
        print(f"  • Staff: {Staff.query.count()}")

if __name__ == '__main__':
    seed_database()
