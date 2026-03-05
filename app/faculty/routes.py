from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.faculty import faculty_bp
from app.models import db, Attendance, Student, Note, Leave, Timetable, Enrollment, Notification
from app.utils.file_handler import save_file_securely
from datetime import datetime
import os

@faculty_bp.route('/dashboard')
@login_required
def dashboard():
    """Faculty dashboard"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    faculty = current_user.faculty
    
    # Get students in faculty's department
    students = Student.query.filter_by(department_id=faculty.department_id).all()
    
    # Pending leaves to review
    pending_leaves = Leave.query.filter_by(status='pending').all()
    
    # Notes uploaded
    notes = Note.query.filter_by(user_id=current_user.id).all()
    
    # Today's timetable for this faculty's department
    today = datetime.utcnow().date()
    day_name = today.strftime('%A')
    todays_timetable = Timetable.query.filter_by(
        department=faculty.department_ref.code,
        day_of_week=day_name
    ).order_by(Timetable.start_time).all()
    
    classes_today = len(todays_timetable)
    next_class = None
    now_time_str = datetime.utcnow().strftime('%H:%M')
    for slot in todays_timetable:
        if slot.start_time > now_time_str:
            next_class = f"{slot.subject} at {slot.start_time}"
            break
    
    stats = {
        'total_students': len(students),
        'pending_leaves': len(pending_leaves),
        'notes_uploaded': len(notes),
        'classes_today': classes_today
    }
    
    # Active notifications relevant to faculty
    notifications = Notification.query.filter(
        Notification.is_active.is_(True),
        Notification.target_audience.in_(['all', 'faculty'])
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return render_template(
        'dashboard/faculty_dashboard.html',
        faculty=faculty,
        stats=stats,
        students=students,
        pending_leaves=pending_leaves,
        todays_timetable=todays_timetable,
        next_class=next_class,
        notifications=notifications,
        today_str=today.strftime('%B %d, %Y')
    )

@faculty_bp.route('/mark-attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    """Mark attendance for students according to timetable"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    faculty = current_user.faculty
    
    if request.method == 'POST':
        timetable_id = request.form.get('timetable_id', type=int)
        attendance_date = request.form.get('attendance_date')
        
        if not timetable_id or not attendance_date:
            flash('Please select a timetable entry and date.', 'danger')
            return redirect(url_for('faculty.mark_attendance'))
        
        # Get the timetable entry
        timetable = Timetable.query.get(timetable_id)
        if not timetable:
            flash('Timetable entry not found.', 'danger')
            return redirect(url_for('faculty.mark_attendance'))
        
        try:
            att_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('faculty.mark_attendance'))
        
        # Get students for this class: enrolled in course, or fallback to dept+semester (same as student timetable)
        enrolled_students = []
        if timetable.course_id:
            enrolled_students = Student.query.join(Enrollment).filter(
                Enrollment.course_id == timetable.course_id,
                Enrollment.status == 'enrolled'
            ).all()
        if not enrolled_students:
            # Fallback: students in same department and semester (class) so faculty can mark attendance
            enrolled_students = Student.query.filter_by(
                department_id=faculty.department_id,
                semester=timetable.semester
            ).all()
        
        # Mark attendance for enrolled students
        for student in enrolled_students:
            status = request.form.get(f'student_{student.id}', 'absent')
            
            # Check if attendance already exists for this timetable and date
            existing = Attendance.query.filter_by(
                student_id=student.id,
                timetable_id=timetable_id,
                date=att_date
            ).first()
            
            if existing:
                existing.status = status
                existing.marked_by = current_user.username
            else:
                attendance = Attendance(
                    student_id=student.id,
                    timetable_id=timetable_id,
                    date=att_date,
                    status=status,
                    marked_by=current_user.username
                )
                db.session.add(attendance)
        
        db.session.commit()
        flash(f'Attendance marked successfully for {att_date}.', 'success')
        return redirect(url_for('faculty.mark_attendance'))
    
    # Get timetable entries for faculty's department
    timetables = Timetable.query.filter_by(department=faculty.department_ref.code).all()
    
    return render_template('attendance/mark_attendance.html', timetables=timetables)

@faculty_bp.route('/upload-notes', methods=['GET', 'POST'])
@login_required
def upload_notes():
    """Upload study notes"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        semester = request.form.get('semester', type=int)
        
        if not title or not subject:
            flash('Title and subject are required.', 'danger')
            return redirect(url_for('faculty.upload_notes'))
        
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('faculty.upload_notes'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('faculty.upload_notes'))
        
        file_path, file_name = save_file_securely(file, 'notes')
        
        if file_path:
            note = Note(
                user_id=current_user.id,
                title=title,
                subject=subject,
                description=description,
                file_path=file_path,
                file_name=file_name,
                department=current_user.faculty.department_ref.code,
                semester=semester
            )
            db.session.add(note)
            db.session.commit()
            
            flash('Notes uploaded successfully.', 'success')
            return redirect(url_for('faculty.upload_notes'))
        else:
            flash('File upload failed.', 'danger')
    
    return render_template('notes/upload_notes.html')

@faculty_bp.route('/my-notes')
@login_required
def my_notes():
    """View uploaded notes"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    notes = Note.query.filter_by(user_id=current_user.id)\
        .order_by(Note.upload_date.desc()).all()
    
    return render_template('notes/faculty_notes.html', notes=notes)

@faculty_bp.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a note"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    note = Note.query.get(note_id)
    
    if not note or note.user_id != current_user.id:
        flash('Note not found or unauthorized.', 'danger')
        return redirect(url_for('faculty.my_notes'))
    
    # Delete file
    if os.path.exists(note.file_path):
        os.remove(note.file_path)
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully.', 'success')
    return redirect(url_for('faculty.my_notes'))
@faculty_bp.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    """Apply for leave"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        leave_type = request.form.get('leave_type', 'General').strip() or 'General'
        reason = request.form.get('reason', '').strip()
        
        if not start_date or not end_date or not leave_type or not reason:
            flash('All fields are required.', 'danger')
            return redirect(url_for('faculty.apply_leave'))
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start >= end:
                flash('End date must be after start date.', 'danger')
                return redirect(url_for('faculty.apply_leave'))
            
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
            return redirect(url_for('faculty.my_leaves'))
        except ValueError:
            flash('Invalid date format.', 'danger')
    
    from app.constants import LEAVE_TYPES
    return render_template('leave/apply_leave.html', leave_types=LEAVE_TYPES)

@faculty_bp.route('/my-leaves')
@login_required
def my_leaves():
    """View my leave applications"""
    if current_user.role != 'faculty':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    leaves = Leave.query.filter_by(user_id=current_user.id)\
        .order_by(Leave.applied_at.desc()).all()
    
    return render_template('leave/student_leaves.html', leaves=leaves)

@faculty_bp.route('/api/course-students/<int:course_id>')
@login_required
def api_course_students(course_id):
    """API endpoint to get students enrolled in a course"""
    from flask import jsonify
    
    if current_user.role != 'faculty':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get students enrolled in the course
    students = Student.query.join(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == 'enrolled'
    ).all()
    
    students_data = [{
        'id': student.id,
        'roll_no': student.roll_no,
        'username': student.user.username,
        'semester': student.semester
    } for student in students]
    
    return jsonify({'students': students_data})


@faculty_bp.route('/api/class-students')
@login_required
def api_class_students():
    """API: students in a class (department + semester). Used when course has no enrollments."""
    from flask import jsonify
    
    if current_user.role != 'faculty':
        return jsonify({'error': 'Unauthorized'}), 403
    
    department = request.args.get('department', '').strip()
    semester = request.args.get('semester', type=int)
    faculty = current_user.faculty
    
    if not department or semester is None:
        return jsonify({'students': []})
    
    # Only allow faculty's own department
    if faculty.department_ref.code != department:
        return jsonify({'students': []})
    
    students = Student.query.filter_by(
        department_id=faculty.department_id,
        semester=semester
    ).all()
    
    students_data = [{
        'id': s.id,
        'roll_no': s.roll_no,
        'username': s.user.username,
        'semester': s.semester
    } for s in students]
    
    return jsonify({'students': students_data})