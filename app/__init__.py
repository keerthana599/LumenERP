from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db, User
import os

login_manager = LoginManager()

def create_app(config_name='development'):
    """Flask application factory"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in first.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create data folder if it doesn't exist (for database)
    # Skip on Vercel (read-only filesystem)
    if not os.getenv('VERCEL'):
        try:
            data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            os.makedirs(data_folder, exist_ok=True)
        except OSError:
            # Silent fail on read-only filesystems
            pass
    
    # Create upload folder if it doesn't exist
    # Skip on Vercel (read-only filesystem)
    if not os.getenv('VERCEL'):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'notes'), exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certificates'), exist_ok=True)
        except OSError:
            # Silent fail on read-only filesystems
            pass
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.student import student_bp
    from app.faculty import faculty_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(admin_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        _create_default_users()
    
    return app

def _create_default_users():
    """Create default admin, faculty, student, and department records if they don't exist"""
    from app.models import User, Student, Faculty, Department
    
    # Create default departments if they don't exist
    departments = [
        {'name': 'Computer Science', 'code': 'CS', 'head': 'Dr. John Smith'},
        {'name': 'Electronics and Communications', 'code': 'EC', 'head': 'Dr. Sarah Johnson'},
        {'name': 'Mechanical Engineering', 'code': 'ME', 'head': 'Dr. Robert Brown'},
        {'name': 'Civil Engineering', 'code': 'CE', 'head': 'Dr. Emily Davis'},
        {'name': 'Information Technology', 'code': 'IT', 'head': 'Dr. Michael Wilson'}
    ]
    
    for dept_info in departments:
        if not Department.query.filter_by(code=dept_info['code']).first():
            dept = Department(
                name=dept_info['name'],
                code=dept_info['code'],
                head=dept_info['head']
            )
            db.session.add(dept)
    
    db.session.commit()
    
    # Default admin (no department needed)
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@erp.edu',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Default faculty
    if not User.query.filter_by(username='faculty').first():
        # Get CS department
        cs_dept = Department.query.filter_by(code='CS').first()
        
        faculty_user = User(
            username='faculty',
            email='faculty@erp.edu',
            role='faculty',
            is_active=True
        )
        faculty_user.set_password('faculty123')
        db.session.add(faculty_user)
        db.session.commit()
        
        if cs_dept:
            faculty = Faculty(
                user_id=faculty_user.id,
                department_id=cs_dept.id,
                designation='Assistant Professor',
                phone='9876543210',
                qualification='PhD',
                specialization='Database Systems'
            )
            db.session.add(faculty)
            db.session.commit()
    
    # Default student
    if not User.query.filter_by(username='student').first():
        # Get CS department
        cs_dept = Department.query.filter_by(code='CS').first()
        
        student_user = User(
            username='student',
            email='student@erp.edu',
            role='student',
            is_active=True
        )
        student_user.set_password('student123')
        db.session.add(student_user)
        db.session.commit()
        
        if cs_dept:
            student = Student(
                user_id=student_user.id,
                roll_no='CS2024001',
                department_id=cs_dept.id,
                semester=4,
                phone='9123456789'
            )
            db.session.add(student)
            db.session.commit()
