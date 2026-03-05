from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import db, Timetable, Staff

@main_bp.route('/')
def home():
    """Home page"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/timetable')
@login_required
def timetable():
    """View timetable"""
    if current_user.role == 'student':
        department = current_user.student.department_ref.code
        semester = current_user.student.semester
    elif current_user.role == 'faculty':
        department = current_user.faculty.department_ref.code
        semester = None
    else:
        department = None
        semester = None
    
    timetables = Timetable.query.all()
    
    if department:
        timetables = [t for t in timetables if t.department == department]
    
    # Build days and time slots from actual data (no hardcoding)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    days_in_data = sorted(set(t.day_of_week for t in timetables if t.day_of_week), key=lambda d: days_order.index(d) if d in days_order else 99)
    time_slots = sorted(set(t.start_time for t in timetables))
    if not time_slots:
        time_slots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    timetables_by_day = {}
    for day in days_order:
        timetables_by_day[day] = [t for t in timetables if t.day_of_week == day]
    
    return render_template('timetable/timetable.html',
                         timetables_by_day=timetables_by_day,
                         days_order=days_order,
                         time_slots=time_slots)

@main_bp.route('/staff')
@login_required
def staff_list():
    """View staff directory"""
    staff = Staff.query.all()
    return render_template('staff/staff_list.html', staff=staff)
