from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    head = db.Column(db.String(100))  # Department head name
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    office = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty = db.relationship('Faculty', backref='department_ref', cascade='all, delete-orphan')
    students = db.relationship('Student', backref='department_ref', cascade='all, delete-orphan')
    courses = db.relationship('Course', backref='department_ref', cascade='all, delete-orphan')
    staff = db.relationship('Staff', backref='department_ref', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)  # Credit hours
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))  # Primary instructor
    max_students = db.Column(db.Integer, default=50)
    room_no = db.Column(db.String(20))
    schedule = db.Column(db.String(255))  # e.g., "Mon,Wed 10:00-11:30"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.code} - {self.name}>'

class Enrollment(db.Model):
    """Student course enrollment"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.String(2))  # A, B, C, D, F
    marks = db.Column(db.Float)  # Out of 100
    status = db.Column(db.String(20), default='enrolled')  # 'enrolled', 'completed', 'dropped'
    enrolled_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='uq_student_course'),)
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.course_id}>'

class User(UserMixin, db.Model):
    """User model for Admin, Faculty, and Students"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'faculty', 'student'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    faculty = db.relationship('Faculty', backref='user', uselist=False, cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='user', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='faculty', cascade='all, delete-orphan')
    uploaded_certificates = db.relationship('Certificate', backref='admin', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', cascade='all, delete-orphan')
    fees = db.relationship('Fee', backref='student', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.roll_no}>'

class Faculty(db.Model):
    """Faculty model"""
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    office = db.Column(db.String(100))
    qualification = db.Column(db.String(100))  # PhD, Masters, etc.
    specialization = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses_taught = db.relationship('Course', backref='instructor', foreign_keys='Course.faculty_id')
    
    def __repr__(self):
        return f'<Faculty {self.user.username}>'

class Attendance(db.Model):
    """Attendance model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    timetable_id = db.Column(db.Integer, db.ForeignKey('timetable.id'), nullable=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # 'present', 'absent', 'leave'
    remarks = db.Column(db.Text)
    marked_by = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'timetable_id', 'date', name='uq_student_timetable_date'),)
    
    # Relationship
    timetable = db.relationship('Timetable', backref='attendance_records')
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date}>'

class Leave(db.Model):
    """Leave application model"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), nullable=False, default='General')  # 'Sick', 'Casual', etc.
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', 'rejected'
    remarks = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(80))
    
    def __repr__(self):
        return f'<Leave {self.user_id} - {self.status}>'

class Fee(db.Model):
    """Fee model"""
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'paid'
    paid_date = db.Column(db.DateTime)
    due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'semester', name='uq_student_semester'),)
    
    def __repr__(self):
        return f'<Fee {self.student_id} - Sem{self.semester}>'

class Note(db.Model):
    """Study notes/materials model"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Note {self.title}>'

class Certificate(db.Model):
    """Certificate model"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    certificate_type = db.Column(db.String(100), nullable=False)  # 'Completion', 'Achievement', etc.
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.Date)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Certificate {self.certificate_type}>'

class Timetable(db.Model):
    """Timetable/Schedule model"""
    __tablename__ = 'timetable'
    
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    day_of_week = db.Column(db.String(15), nullable=False)  # 'Monday', 'Tuesday', etc.
    start_time = db.Column(db.String(10), nullable=False)  # 'HH:MM'
    end_time = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    faculty_name = db.Column(db.String(100))
    room_no = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    course = db.relationship('Course', backref='timetables')
    
    def __repr__(self):
        return f'<Timetable {self.department} - {self.day_of_week}>'

class Staff(db.Model):
    """Non-faculty staff model"""
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    office = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    """Notification model for system-wide announcements"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'announcement', 'alert', 'info', 'warning'
    target_audience = db.Column(db.String(50), nullable=False)  # 'all', 'students', 'faculty', 'admin', 'department'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)  # If targeting specific department
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration date
    
    # Relationship
    department = db.relationship('Department', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'
    
    def __repr__(self):
        return f'<Staff {self.name}>'
