from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.student import student_bp
from app.models import db, Attendance, Leave, Fee, Note, Certificate, Notification, Enrollment
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import os

from app.constants import LEAVE_TYPES

# Grade letter to points for CGPA (4.0 scale)
GRADE_POINTS = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}


def _time_ago(dt):
    """Return human-readable time ago string for a datetime."""
    if not dt:
        return ''
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'Just now'
    if seconds < 3600:
        mins = int(seconds / 60)
        return f'{mins} minute{"s" if mins != 1 else ""} ago'
    if seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    if seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days != 1 else ""} ago'
    if seconds < 2592000:
        weeks = int(seconds / 604800)
        return f'{weeks} week{"s" if weeks != 1 else ""} ago'
    if seconds < 31536000:
        months = int(seconds / 2592000)
        return f'{months} month{"s" if months != 1 else ""} ago'
    years = int(seconds / 31536000)
    return f'{years} year{"s" if years != 1 else ""} ago'


@student_bp.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard with live data"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    now = datetime.utcnow()
    today = now.date()
    
    # Attendance stats (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    attendance_records = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.date >= thirty_days_ago
    ).all()
    total_days = len(attendance_records)
    present_days = len([a for a in attendance_records if a.status == 'present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Fee details and nearest due date for pending fees
    fees = Fee.query.filter_by(student_id=student.id).all()
    total_fees = sum(f.amount for f in fees)
    pending_fees = sum(f.amount for f in fees if f.status == 'pending')
    pending_fee_records = [f for f in fees if f.status == 'pending' and f.due_date]
    fee_due_date = None
    if pending_fee_records:
        fee_due_date = min(f.due_date for f in pending_fee_records)
    
    # New notes count: notes for this student's department/semester uploaded in last 7 days
    seven_days_ago = now - timedelta(days=7)
    dept_code = student.department_ref.code if student.department_ref else None
    new_notes_count = Note.query.filter(
        Note.upload_date >= seven_days_ago,
        or_(
            Note.department == dept_code,
            Note.semester == student.semester,
            Note.department.is_(None)
        )
    ).count()
    
    # CGPA from enrollments with grades
    enrollments_with_grade = Enrollment.query.filter(
        Enrollment.student_id == student.id,
        Enrollment.grade != None,
        Enrollment.grade != ''
    ).all()
    cgpa = None
    if enrollments_with_grade:
        points = []
        for e in enrollments_with_grade:
            g = (e.grade or '').strip().upper()
            if g and g[0] in GRADE_POINTS:
                points.append(GRADE_POINTS[g[0]])
        if points:
            cgpa = round(sum(points) / len(points), 1)
    
    # Notifications: active, for students (all/students/department), not expired
    notifications_query = Notification.query.filter(
        Notification.is_active == True,
        or_(
            Notification.target_audience.in_(['all', 'students']),
            (Notification.target_audience == 'department') & (Notification.department_id == student.department_id)
        ),
        (Notification.expires_at.is_(None)) | (Notification.expires_at > now)
    ).order_by(Notification.created_at.desc()).limit(10)
    notifications_raw = notifications_query.all()
    notifications = [
        {'title': n.title, 'message': n.message, 'time_ago': _time_ago(n.created_at), 'created_at': n.created_at}
        for n in notifications_raw
    ]
    
    return render_template('dashboard/student_dashboard.html',
                         student=student,
                         attendance_percentage=round(attendance_percentage, 2),
                         fees=fees,
                         total_fees=total_fees,
                         pending_fees=pending_fees,
                         fee_due_date=fee_due_date,
                         new_notes_count=new_notes_count,
                         cgpa=cgpa,
                         notifications=notifications)

@student_bp.route('/attendance')
@login_required
def view_attendance():
    """View student attendance"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    page = request.args.get('page', 1, type=int)
    
    attendance_records = Attendance.query.filter_by(student_id=student.id)\
        .order_by(Attendance.date.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('attendance/view_attendance.html', attendance=attendance_records)

@student_bp.route('/fees')
@login_required
def fees():
    """View fees"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    fee_records = Fee.query.filter_by(student_id=student.id).all()
    
    total_fees = sum(f.amount for f in fee_records)
    paid_fees = sum(f.amount for f in fee_records if f.status == 'paid')
    pending_fees = total_fees - paid_fees
    
    return render_template('fees/fees.html',
                         fees=fee_records,
                         total_fees=total_fees,
                         paid_fees=paid_fees,
                         pending_fees=pending_fees)

@student_bp.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    """Apply for leave"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        leave_type = request.form.get('leave_type', 'General').strip() or 'General'
        reason = request.form.get('reason', '').strip()
        
        if not start_date or not end_date or not leave_type or not reason:
            flash('All fields are required.', 'danger')
            return redirect(url_for('student.apply_leave'))
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start >= end:
                flash('End date must be after start date.', 'danger')
                return redirect(url_for('student.apply_leave'))
            
            leave = Leave(
                user_id=current_user.id,
                start_date=start,
                end_date=end,
                leave_type=leave_type,
                reason=reason,
                status='pending'
            )
            db.session.add(leave)
            db.session.commit()
            
            flash('Leave application submitted successfully.', 'success')
            return redirect(url_for('student.my_leaves'))
        except ValueError:
            flash('Invalid date format.', 'danger')
    
    return render_template('leave/apply_leave.html', leave_types=LEAVE_TYPES)

@student_bp.route('/my-leaves')
@login_required
def my_leaves():
    """View my leave applications"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    leaves = Leave.query.filter_by(user_id=current_user.id)\
        .order_by(Leave.applied_at.desc()).all()
    
    return render_template('leave/student_leaves.html', leaves=leaves)

@student_bp.route('/notes')
@login_required
def view_notes():
    """View study notes"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    
    # Get notes for student's department and semester
    notes = Note.query.filter(
        (Note.department == student.department_ref.code) |
        (Note.semester == student.semester) |
        (Note.department == None)
    ).order_by(Note.upload_date.desc()).all()
    
    return render_template('notes/view_notes.html', notes=notes)


@student_bp.route('/download-note/<int:note_id>')
@login_required
def download_note(note_id):
    """Download a note file (only if student has access by dept/semester)."""
    if current_user.role != 'student':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('auth.login'))
    student = current_user.student
    note = Note.query.get_or_404(note_id)
    dept_code = student.department_ref.code if student.department_ref else None
    # Same visibility as view_notes: dept match, semester match, or no dept filter
    can_access = (
        note.department is None or
        note.department == dept_code or
        note.semester == student.semester
    )
    if not can_access:
        flash('You do not have access to this note.', 'danger')
        return redirect(url_for('student.view_notes'))
    if not os.path.isfile(note.file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('student.view_notes'))
    try:
        note.download_count = (note.download_count or 0) + 1
        db.session.commit()
    except Exception:
        db.session.rollback()
    return send_file(
        note.file_path,
        as_attachment=True,
        download_name=note.file_name or 'note'
    )


@student_bp.route('/certificates')
@login_required
def certificates():
    """Download certificates"""
    if current_user.role != 'student':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    certificates = Certificate.query.filter_by(student_id=student.id).all()
    
    return render_template('certificates/download_cert.html', certificates=certificates)


@student_bp.route('/download-certificate/<int:cert_id>')
@login_required
def download_certificate(cert_id):
    """Download a certificate file (only for the owning student)."""
    if current_user.role != 'student':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('auth.login'))
    student = current_user.student
    cert = Certificate.query.get_or_404(cert_id)
    if cert.student_id != student.id:
        flash('You do not have access to this certificate.', 'danger')
        return redirect(url_for('student.certificates'))
    if not os.path.isfile(cert.file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('student.certificates'))
    return send_file(
        cert.file_path,
        as_attachment=True,
        download_name=cert.file_name or 'certificate'
    )
