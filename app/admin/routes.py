from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import db, User, Student, Faculty, Leave, Certificate, Timetable, Staff, Note, Fee, Attendance, Department, Course, Enrollment, Notification
from app.utils.file_handler import save_file_securely
from datetime import datetime
import os

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    stats = {
        'total_students': Student.query.count(),
        'total_faculty': Faculty.query.count(),
        'total_users': User.query.count(),
        'pending_leaves': Leave.query.filter_by(status='pending').count(),
        'pending_fees': Fee.query.filter_by(status='pending').count(),
        'certificates_issued': Certificate.query.count()
    }
    
    pending_leaves = Leave.query.filter_by(status='pending').all()
    
    # Active notifications relevant to admin
    notifications = Notification.query.filter(
        Notification.is_active.is_(True),
        Notification.target_audience.in_(['all', 'admin'])
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return render_template(
        'dashboard/admin_dashboard.html',
        stats=stats,
        pending_leaves=pending_leaves,
        notifications=notifications
    )

@admin_bp.route('/users')
@login_required
def users():
    """Manage users"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    users = query.paginate(page=page, per_page=10)
    
    return render_template('admin/users.html', users=users, role_filter=role_filter)

@admin_bp.route('/students')
@login_required
def students():
    """Manage students"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    dept_filter = request.args.get('department', 'all')
    
    query = Student.query
    if dept_filter != 'all':
        query = query.filter_by(department_id=int(dept_filter))
    
    students = query.paginate(page=page, per_page=10)
    
    departments = Department.query.all()
    
    return render_template('admin/students.html', 
                         students=students,
                         dept_filter=dept_filter,
                         departments=departments)

@admin_bp.route('/manage-leaves', methods=['GET', 'POST'])
@login_required
def manage_leaves():
    """Approve/Reject leave applications"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')
    
    query = Leave.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    leaves = query.paginate(page=page, per_page=10)
    
    return render_template('leave/manage_leave.html', leaves=leaves, status_filter=status_filter)

@admin_bp.route('/approve-leave/<int:leave_id>', methods=['POST'])
@login_required
def approve_leave(leave_id):
    """Approve leave"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    leave = Leave.query.get(leave_id)
    
    if not leave:
        flash('Leave not found.', 'danger')
        return redirect(url_for('admin.manage_leaves'))
    
    leave.status = 'approved'
    leave.resolved_by = current_user.username
    leave.resolved_at = datetime.utcnow()
    db.session.commit()
    
    flash('Leave approved.', 'success')
    return redirect(url_for('admin.manage_leaves'))

@admin_bp.route('/reject-leave/<int:leave_id>', methods=['POST'])
@login_required
def reject_leave(leave_id):
    """Reject leave"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    leave = Leave.query.get(leave_id)
    remarks = request.form.get('remarks', '')
    
    if not leave:
        flash('Leave not found.', 'danger')
        return redirect(url_for('admin.manage_leaves'))
    
    leave.status = 'rejected'
    leave.remarks = remarks
    leave.resolved_by = current_user.username
    leave.resolved_at = datetime.utcnow()
    db.session.commit()
    
    flash('Leave rejected.', 'success')
    return redirect(url_for('admin.manage_leaves'))

@admin_bp.route('/upload-certificate', methods=['GET', 'POST'])
@login_required
def upload_certificate():
    """Upload certificate for student"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        cert_type = request.form.get('certificate_type', '').strip()
        issue_date = request.form.get('issue_date')
        description = request.form.get('description', '').strip()
        
        if not student_id or not cert_type:
            flash('Student and certificate type are required.', 'danger')
            return redirect(url_for('admin.upload_certificate'))
        
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('admin.upload_certificate'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('admin.upload_certificate'))
        
        student = Student.query.get(student_id)
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('admin.upload_certificate'))
        
        file_path, file_name = save_file_securely(file, 'certificates')
        
        if file_path:
            try:
                issue_dt = datetime.strptime(issue_date, '%Y-%m-%d').date() if issue_date else None
            except ValueError:
                issue_dt = None
            
            certificate = Certificate(
                user_id=current_user.id,
                student_id=student_id,
                certificate_type=cert_type,
                file_path=file_path,
                file_name=file_name,
                issue_date=issue_dt,
                description=description
            )
            db.session.add(certificate)
            db.session.commit()
            
            flash('Certificate uploaded successfully.', 'success')
            return redirect(url_for('admin.upload_certificate'))
        else:
            flash('File upload failed.', 'danger')
    
    students = Student.query.all()
    
    return render_template('certificates/upload_cert.html', students=students)

@admin_bp.route('/manage-timetable')
@login_required
def manage_timetable():
    """Manage timetable"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get all timetables organized by department and semester
    timetables = Timetable.query.all()
    
    # Organize by department and semester
    organized = {}
    for tt in timetables:
        key = f"{tt.department}-{tt.semester}"
        if key not in organized:
            organized[key] = {'department': tt.department, 'semester': tt.semester, 'slots': []}
        organized[key]['slots'].append(tt)
    
    # Sort by day of week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for key in organized:
        organized[key]['slots'].sort(key=lambda x: days_order.index(x.day_of_week) if x.day_of_week in days_order else 999)
    
    faculties = Faculty.query.all()
    departments = Department.query.order_by(Department.code).all()
    semesters = sorted(set(c.semester for c in Course.query.all())) or list(range(1, 9))
    
    return render_template('admin/manage_timetable.html',
                         organized_timetables=organized,
                         faculties=faculties,
                         departments=departments,
                         semesters=semesters)

@admin_bp.route('/add-timetable', methods=['GET', 'POST'])
@login_required
def add_timetable():
    """Add timetable entry"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', type=int)
        course_id = request.form.get('course_id', type=int)
        day_of_week = request.form.get('day_of_week', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        subject = request.form.get('subject', '').strip()
        faculty_id = request.form.get('faculty_id', type=int)
        room_no = request.form.get('room_no', '').strip()
        
        if not all([department, semester, course_id, day_of_week, start_time, end_time, subject]):
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('admin.add_timetable'))

        course = Course.query.get(course_id)
        if not course or course.department_ref.code != department:
            flash('Invalid course; ensure it belongs to the selected department.', 'danger')
            return redirect(url_for('admin.add_timetable'))
        
        # Get faculty name if faculty_id is provided
        faculty_name = ''
        if faculty_id:
            faculty = Faculty.query.get(faculty_id)
            if faculty:
                faculty_name = faculty.user.username
        
        timetable = Timetable(
            department=department,
            semester=semester,
            course_id=course_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            subject=subject,
            faculty_name=faculty_name,
            room_no=room_no
        )
        
        db.session.add(timetable)
        db.session.commit()
        
        flash('Timetable entry added successfully.', 'success')
        return redirect(url_for('admin.manage_timetable'))
    
    # Get query parameters for pre-selection
    pre_dept = request.args.get('dept', '')
    pre_sem = request.args.get('sem', type=int)
    
    faculties = Faculty.query.all()
    departments = Department.query.order_by(Department.code).all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    semesters = list(range(1, 9))  # 1-8 so admin can select any semester
    courses = Course.query.all()  # JS filters by department + semester

    return render_template('admin/add_timetable.html',
                         faculties=faculties,
                         departments=departments,
                         days=days,
                         semesters=semesters,
                         courses=courses,
                         pre_dept=pre_dept,
                         pre_sem=pre_sem)

@admin_bp.route('/reports')
@login_required
def reports():
    """System reports"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get report statistics
    total_students = Student.query.count()
    
    # Calculate attendance statistics
    students = Student.query.all()
    attendance_percentages = []
    below_75_count = 0
    perfect_attendance_count = 0
    
    for student in students:
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        if attendance_records:
            present_count = sum(1 for a in attendance_records if a.status == 'present')
            total_count = len(attendance_records)
            percentage = (present_count / total_count) * 100 if total_count > 0 else 0
            attendance_percentages.append(percentage)
            
            if percentage < 75:
                below_75_count += 1
            elif percentage == 100:
                perfect_attendance_count += 1
    
    # Calculate average attendance
    total_attendance_percentage = sum(attendance_percentages) / len(attendance_percentages) if attendance_percentages else 0
    
    # Fees stats
    total_fees = Fee.query.all()
    pending_fees_count = Fee.query.filter_by(status='pending').count()
    collected_fees = sum(f.amount for f in total_fees if f.status == 'paid')
    
    report_data = {
        'average_attendance': round(total_attendance_percentage, 1),
        'below_75_students': below_75_count,
        'perfect_attendance': perfect_attendance_count,
        'total_students': total_students,
        'pending_fees': pending_fees_count,
        'collected_fees': collected_fees
    }
    
    return render_template('admin/reports.html', report_data=report_data)

@admin_bp.route('/manage-staff')
@login_required
def manage_staff():
    """Manage staff"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    staff = Staff.query.all()
    
    return render_template('admin/manage_staff.html', staff=staff)

@admin_bp.route('/add-staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    """Add new staff member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        designation = request.form.get('designation', '').strip()
        department_id = request.form.get('department_id', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        office = request.form.get('office', '').strip()
        
        if not name or not designation or not department_id:
            flash('Name, designation, and department are required.', 'danger')
            return redirect(url_for('admin.add_staff'))
        
        try:
            department_id = int(department_id)
            dept = Department.query.get(department_id)
            
            if not dept:
                flash('Selected department does not exist.', 'danger')
                return redirect(url_for('admin.add_staff'))
            
            staff = Staff(
                name=name,
                designation=designation,
                department_id=department_id,
                email=email,
                phone=phone,
                office=office
            )
            db.session.add(staff)
            db.session.commit()
            
            flash('Staff member added successfully.', 'success')
            return redirect(url_for('admin.manage_staff'))
        except Exception as e:
            flash(f'Error adding staff member: {str(e)}', 'danger')
            return redirect(url_for('admin.add_staff'))
    
    departments = Department.query.all()
    return render_template('admin/add_staff.html', departments=departments)

@admin_bp.route('/edit-staff/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    """Edit staff member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    staff = Staff.query.get(staff_id)
    
    if not staff:
        flash('Staff not found.', 'danger')
        return redirect(url_for('admin.manage_staff'))
    
    if request.method == 'POST':
        staff.name = request.form.get('name', '').strip()
        staff.designation = request.form.get('designation', '').strip()
        department_id = request.form.get('department_id', '').strip()
        staff.email = request.form.get('email', '').strip()
        staff.phone = request.form.get('phone', '').strip()
        staff.office = request.form.get('office', '').strip()
        
        if not staff.name or not staff.designation or not department_id:
            flash('Name, designation, and department are required.', 'danger')
            return redirect(url_for('admin.edit_staff', staff_id=staff_id))
        
        try:
            department_id = int(department_id)
            dept = Department.query.get(department_id)
            
            if not dept:
                flash('Selected department does not exist.', 'danger')
                return redirect(url_for('admin.edit_staff', staff_id=staff_id))
            
            staff.department_id = department_id
            db.session.commit()
            
            flash('Staff member updated successfully.', 'success')
            return redirect(url_for('admin.manage_staff'))
        except Exception as e:
            flash(f'Error updating staff member: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_staff', staff_id=staff_id))
    
    departments = Department.query.all()
    return render_template('admin/edit_staff.html', staff=staff, departments=departments)

@admin_bp.route('/delete-staff/<int:staff_id>', methods=['POST'])
@login_required
def delete_staff(staff_id):
    """Delete staff member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    staff = Staff.query.get(staff_id)
    
    if not staff:
        flash('Staff not found.', 'danger')
        return redirect(url_for('admin.manage_staff'))
    
    db.session.delete(staff)
    db.session.commit()
    
    flash('Staff member deleted.', 'success')
    return redirect(url_for('admin.manage_staff'))

# ==================== DEPARTMENT MANAGEMENT ====================

@admin_bp.route('/departments')
@login_required
def manage_departments():
    """Manage departments"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    departments = Department.query.paginate(page=page, per_page=10)
    
    return render_template('admin/manage_departments.html', departments=departments)

@admin_bp.route('/add-department', methods=['GET', 'POST'])
@login_required
def add_department():
    """Add new department"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        description = request.form.get('description', '').strip()
        head = request.form.get('head', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        office = request.form.get('office', '').strip()
        
        if not name or not code:
            flash('Department name and code are required.', 'danger')
            return redirect(url_for('admin.add_department'))
        
        if Department.query.filter_by(code=code).first():
            flash('Department code already exists.', 'danger')
            return redirect(url_for('admin.add_department'))
        
        department = Department(
            name=name,
            code=code,
            description=description,
            head=head,
            email=email,
            phone=phone,
            office=office
        )
        db.session.add(department)
        db.session.commit()
        
        flash('Department added successfully.', 'success')
        return redirect(url_for('admin.manage_departments'))
    
    return render_template('admin/add_department.html')

@admin_bp.route('/edit-department/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    """Edit department"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    department = Department.query.get_or_404(dept_id)
    
    if request.method == 'POST':
        department.name = request.form.get('name', '').strip()
        department.code = request.form.get('code', '').strip()
        department.description = request.form.get('description', '').strip()
        department.head = request.form.get('head', '').strip()
        department.email = request.form.get('email', '').strip()
        department.phone = request.form.get('phone', '').strip()
        department.office = request.form.get('office', '').strip()
        
        db.session.commit()
        flash('Department updated successfully.', 'success')
        return redirect(url_for('admin.manage_departments'))
    
    return render_template('admin/edit_department.html', department=department)

@admin_bp.route('/delete-department/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    """Delete department"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    department = Department.query.get_or_404(dept_id)
    
    # Cascade delete: related students, faculty, courses, and staff are removed by SQLAlchemy
    db.session.delete(department)
    db.session.commit()
    
    flash('Department deleted successfully.', 'success')
    return redirect(url_for('admin.manage_departments'))

# ==================== COURSE MANAGEMENT ====================

@admin_bp.route('/courses')
@login_required
def manage_courses():
    """Manage courses"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    dept_filter = request.args.get('department', 'all')
    
    query = Course.query
    if dept_filter != 'all':
        query = query.filter_by(department_id=dept_filter)
    
    courses = query.paginate(page=page, per_page=10)
    departments = Department.query.all()
    
    return render_template('admin/manage_courses.html', 
                         courses=courses,
                         departments=departments,
                         dept_filter=dept_filter)

@admin_bp.route('/add-course', methods=['GET', 'POST'])
@login_required
def add_course():
    """Add new course"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        credits = request.form.get('credits', type=int, default=3)
        semester = request.form.get('semester', type=int)
        department_id = request.form.get('department_id', type=int)
        faculty_id = request.form.get('faculty_id', type=int)
        max_students = request.form.get('max_students', type=int, default=50)
        room_no = request.form.get('room_no', '').strip()
        schedule = request.form.get('schedule', '').strip()
        
        if not code or not name or not semester or not department_id:
            flash('Code, name, semester, and department are required.', 'danger')
            return redirect(url_for('admin.add_course'))
        
        if Course.query.filter_by(code=code).first():
            flash('Course code already exists.', 'danger')
            return redirect(url_for('admin.add_course'))
        
        course = Course(
            code=code,
            name=name,
            description=description,
            credits=credits,
            semester=semester,
            department_id=department_id,
            faculty_id=faculty_id if faculty_id else None,
            max_students=max_students,
            room_no=room_no,
            schedule=schedule
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course added successfully.', 'success')
        return redirect(url_for('admin.manage_courses'))
    
    departments = Department.query.all()
    faculty = Faculty.query.all()
    
    return render_template('admin/add_course.html', 
                         departments=departments,
                         faculty=faculty)

@admin_bp.route('/edit-course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit course"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.code = request.form.get('code', '').strip()
        course.name = request.form.get('name', '').strip()
        course.description = request.form.get('description', '').strip()
        course.credits = request.form.get('credits', type=int, default=3)
        course.semester = request.form.get('semester', type=int)
        course.department_id = request.form.get('department_id', type=int)
        faculty_id = request.form.get('faculty_id', type=int)
        course.faculty_id = faculty_id if faculty_id else None
        course.max_students = request.form.get('max_students', type=int, default=50)
        course.room_no = request.form.get('room_no', '').strip()
        course.schedule = request.form.get('schedule', '').strip()
        
        db.session.commit()
        flash('Course updated successfully.', 'success')
        return redirect(url_for('admin.manage_courses'))
    
    departments = Department.query.all()
    faculty = Faculty.query.all()
    
    return render_template('admin/edit_course.html', 
                         course=course,
                         departments=departments,
                         faculty=faculty)

@admin_bp.route('/delete-course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete course"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    course = Course.query.get_or_404(course_id)
    
    # Delete all enrollments first
    Enrollment.query.filter_by(course_id=course_id).delete()
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('admin.manage_courses'))

# ==================== FACULTY MANAGEMENT ====================

@admin_bp.route('/faculty')
@login_required
def manage_faculty():
    """Manage faculty"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    dept_filter = request.args.get('department', 'all')
    
    query = Faculty.query
    if dept_filter != 'all':
        query = query.filter_by(department_id=dept_filter)
    
    faculty = query.paginate(page=page, per_page=10)
    departments = Department.query.all()
    
    return render_template('admin/manage_faculty.html',
                         faculty=faculty,
                         departments=departments,
                         dept_filter=dept_filter)

@admin_bp.route('/add-faculty', methods=['GET', 'POST'])
@login_required
def add_faculty():
    """Add faculty member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        department_id = request.form.get('department_id', type=int)
        designation = request.form.get('designation', '').strip()
        phone = request.form.get('phone', '').strip()
        office = request.form.get('office', '').strip()
        qualification = request.form.get('qualification', '').strip()
        specialization = request.form.get('specialization', '').strip()
        
        if not all([username, email, password, department_id, designation]):
            flash('Username, email, password, department, and designation are required.', 'danger')
            return redirect(url_for('admin.add_faculty'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.add_faculty'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.add_faculty'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            role='faculty',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create faculty record
        faculty = Faculty(
            user_id=user.id,
            department_id=department_id,
            designation=designation,
            phone=phone,
            office=office,
            qualification=qualification,
            specialization=specialization
        )
        db.session.add(faculty)
        db.session.commit()
        
        flash('Faculty member added successfully.', 'success')
        return redirect(url_for('admin.manage_faculty'))
    
    departments = Department.query.all()
    
    return render_template('admin/add_faculty.html', departments=departments)

@admin_bp.route('/edit-faculty/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    """Edit faculty member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    faculty = Faculty.query.get_or_404(faculty_id)
    
    if request.method == 'POST':
        faculty.user.email = request.form.get('email', '').strip()
        faculty.department_id = request.form.get('department_id', type=int)
        faculty.designation = request.form.get('designation', '').strip()
        faculty.phone = request.form.get('phone', '').strip()
        faculty.office = request.form.get('office', '').strip()
        faculty.qualification = request.form.get('qualification', '').strip()
        faculty.specialization = request.form.get('specialization', '').strip()
        
        db.session.commit()
        flash('Faculty member updated successfully.', 'success')
        return redirect(url_for('admin.manage_faculty'))
    
    departments = Department.query.all()
    
    return render_template('admin/edit_faculty.html', 
                         faculty=faculty,
                         departments=departments)

@admin_bp.route('/delete-faculty/<int:faculty_id>', methods=['POST'])
@login_required
def delete_faculty(faculty_id):
    """Delete faculty member"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    faculty = Faculty.query.get_or_404(faculty_id)
    user = faculty.user
    
    # Delete faculty record (cascades to delete user)
    db.session.delete(faculty)
    db.session.delete(user)
    db.session.commit()
    
    flash('Faculty member deleted successfully.', 'success')
    return redirect(url_for('admin.manage_faculty'))

# ==================== STUDENT MANAGEMENT ====================

@admin_bp.route('/manage-students')
@login_required
def manage_students():
    """Manage students"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    dept_filter = request.args.get('department', 'all')
    
    query = Student.query
    if dept_filter != 'all':
        query = query.filter_by(department_id=dept_filter)
    
    students = query.paginate(page=page, per_page=10)
    departments = Department.query.all()
    
    return render_template('admin/manage_students.html',
                         students=students,
                         departments=departments,
                         dept_filter=dept_filter)


@admin_bp.route('/sync-enrollments', methods=['POST'])
@login_required
def sync_enrollments():
    """Sync student-course enrollments: link each student to all courses in their department and semester."""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    added = 0
    for student in Student.query.all():
        for course in Course.query.filter_by(
            department_id=student.department_id,
            semester=student.semester
        ).all():
            if not Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first():
                db.session.add(Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    status='enrolled'
                ))
                added += 1
    db.session.commit()
    flash(f'Sync complete. Added {added} enrollment(s). Students are now linked to courses by department and semester.', 'success')
    return redirect(url_for('admin.manage_students'))


@admin_bp.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add student"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        roll_no = request.form.get('roll_no', '').strip()
        department_id = request.form.get('department_id', type=int)
        semester = request.form.get('semester', type=int)
        course_id = request.form.get('course_id', type=int)
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        if not all([username, email, password, roll_no, department_id, semester]):
            flash('Username, email, password, roll number, department, and semester are required.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        if Student.query.filter_by(roll_no=roll_no).first():
            flash('Roll number already exists.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            role='student',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create student record
        student = Student(
            user_id=user.id,
            roll_no=roll_no,
            department_id=department_id,
            semester=semester,
            phone=phone,
            address=address
        )
        db.session.add(student)
        db.session.commit()
        
        # Create enrollment if course is selected
        if course_id:
            course = Course.query.get(course_id)
            if course:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course_id
                )
                db.session.add(enrollment)
                db.session.commit()
        
        flash('Student added successfully.', 'success')
        return redirect(url_for('admin.manage_students'))
    
    departments = Department.query.all()
    courses = Course.query.all()
    semesters = [1, 2, 3, 4, 5, 6, 7, 8]
    
    return render_template('admin/add_student.html', 
                         departments=departments,
                         courses=courses,
                         semesters=semesters)

@admin_bp.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        student.user.email = request.form.get('email', '').strip()
        student.roll_no = request.form.get('roll_no', '').strip()
        student.department_id = request.form.get('department_id', type=int)
        student.semester = request.form.get('semester', type=int)
        student.phone = request.form.get('phone', '').strip()
        student.address = request.form.get('address', '').strip()
        
        # Handle course enrollment
        course_id = request.form.get('course_id', type=int)
        if course_id:
            # Check if student is already enrolled in this course
            existing_enrollment = Enrollment.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first()
            
            if not existing_enrollment:
                # Remove existing enrollments if updating to a new course
                Enrollment.query.filter_by(student_id=student_id).delete()
                
                # Create new enrollment
                enrollment = Enrollment(
                    student_id=student_id,
                    course_id=course_id
                )
                db.session.add(enrollment)
        else:
            # Clear enrollment if no course selected
            Enrollment.query.filter_by(student_id=student_id).delete()
        
        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('admin.manage_students'))
    
    departments = Department.query.all()
    courses = Course.query.all()
    semesters = [1, 2, 3, 4, 5, 6, 7, 8]
    
    return render_template('admin/edit_student.html',
                         student=student,
                         departments=departments,
                         courses=courses,
                         semesters=semesters)

@admin_bp.route('/delete-student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete student"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(student_id)
    user = student.user
    
    # Delete student record (cascades to delete enrollments, fees, etc.)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('admin.manage_students'))

# Notification Management Routes

@admin_bp.route('/notifications')
@login_required
def manage_notifications():
    """Manage system notifications"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=15)
    
    return render_template('admin/manage_notifications.html', notifications=notifications)

@admin_bp.route('/add-notification', methods=['GET', 'POST'])
@login_required
def add_notification():
    """Create a new notification"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        notification_type = request.form.get('notification_type', 'info')
        target_audience = request.form.get('target_audience', 'all')
        department_id = request.form.get('department_id', type=int)
        expires_at_str = request.form.get('expires_at', '')
        
        if not title or not message:
            flash('Title and message are required.', 'danger')
            return redirect(url_for('admin.add_notification'))
        
        expires_at = None
        if expires_at_str:
            try:
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid expiration date format.', 'danger')
                return redirect(url_for('admin.add_notification'))
        
        # Validate department selection
        if target_audience == 'department' and not department_id:
            flash('Please select a department when targeting specific department.', 'danger')
            return redirect(url_for('admin.add_notification'))
        
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            target_audience=target_audience,
            department_id=department_id if target_audience == 'department' else None,
            created_by=current_user.username,
            expires_at=expires_at
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Notification created successfully.', 'success')
        return redirect(url_for('admin.manage_notifications'))
    
    departments = Department.query.all()
    return render_template('admin/add_notification.html', departments=departments)

@admin_bp.route('/edit-notification/<int:notification_id>', methods=['GET', 'POST'])
@login_required
def edit_notification(notification_id):
    """Edit an existing notification"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    notification = Notification.query.get_or_404(notification_id)
    
    if request.method == 'POST':
        notification.title = request.form.get('title', '').strip()
        notification.message = request.form.get('message', '').strip()
        notification.notification_type = request.form.get('notification_type', 'info')
        notification.target_audience = request.form.get('target_audience', 'all')
        
        # Handle expiration date
        expires_at_str = request.form.get('expires_at', '')
        if expires_at_str:
            try:
                notification.expires_at = datetime.strptime(expires_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid expiration date format.', 'danger')
                return redirect(url_for('admin.edit_notification', notification_id=notification_id))
        else:
            notification.expires_at = None
        
        # Handle department selection
        if notification.target_audience == 'department':
            department_id = request.form.get('department_id', type=int)
            if not department_id:
                flash('Please select a department when targeting specific department.', 'danger')
                return redirect(url_for('admin.edit_notification', notification_id=notification_id))
            notification.department_id = department_id
        else:
            notification.department_id = None
        
        # Toggle active status
        is_active = request.form.get('is_active') == 'on'
        notification.is_active = is_active
        
        db.session.commit()
        
        flash('Notification updated successfully.', 'success')
        return redirect(url_for('admin.manage_notifications'))
    
    departments = Department.query.all()
    return render_template('admin/edit_notification.html', 
                         notification=notification, 
                         departments=departments)

@admin_bp.route('/delete-notification/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    
    flash('Notification deleted successfully.', 'success')
    return redirect(url_for('admin.manage_notifications'))
