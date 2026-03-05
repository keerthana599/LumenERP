"""
Generate a PDF document that explains the working of the LumenERP (College ERP) project.
Run from project root: python scripts/generate_project_documentation_pdf.py
Requires: pip install reportlab
"""
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
    )
except ImportError:
    print("Please install reportlab: pip install reportlab")
    sys.exit(1)


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=12,
        textColor=colors.HexColor('#1e3a5f'),
    )
    heading1_style = ParagraphStyle(
        name='CustomH1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor('#2563eb'),
    )
    heading2_style = ParagraphStyle(
        name='CustomH2',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor('#1e40af'),
    )
    body_style = ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        name='Bullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=4,
    )

    def p(text, style=body_style):
        story.append(Paragraph(text.replace('\n', '<br/>'), style))
        story.append(Spacer(1, 4))

    def h1(text):
        story.append(Paragraph(text, heading1_style))
        story.append(Spacer(1, 6))

    def h2(text):
        story.append(Paragraph(text, heading2_style))
        story.append(Spacer(1, 4))

    # ----- Title Page -----
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("LumenERP", title_style))
    story.append(Paragraph("College ERP System", ParagraphStyle(
        name='Subtitle', parent=styles['Normal'], fontSize=14, spaceAfter=6
    )))
    story.append(Spacer(1, 0.3*inch))
    p("Project Working &amp; Architecture Documentation")
    p("A comprehensive guide to how the system works, its components, and user workflows.")
    story.append(Spacer(1, 0.5*inch))
    p("Version 1.0 | March 2026")
    story.append(PageBreak())

    # ----- 1. Introduction -----
    h1("1. Introduction")
    p("LumenERP is a web-based Enterprise Resource Planning (ERP) system designed for colleges and educational institutions. It manages student data, attendance, fees, leaves, study materials, certificates, timetables, and staff through role-based portals for Admin, Faculty, and Students.")
    p("The application is built with Python Flask on the backend, SQLite for storage, and uses Tailwind CSS for a responsive frontend. Access is controlled by role: Admin, Faculty, or Student.")
    story.append(Spacer(1, 6))

    # ----- 2. Technology Stack -----
    h1("2. Technology Stack")
    h2("Backend")
    p("• Python 3.x – Server language<br/>• Flask 2.3.3 – Web framework and routing<br/>• Flask-SQLAlchemy – ORM for database operations<br/>• Flask-Login – Session-based authentication<br/>• SQLite3 – Database (file: data/erp_system.db)<br/>• Werkzeug – Password hashing and utilities")
    h2("Frontend")
    p("• HTML5 &amp; Jinja2 templates – Page structure and dynamic content<br/>• Tailwind CSS – Responsive layout and styling<br/>• JavaScript – Client-side behavior<br/>• Font Awesome – Icons")
    story.append(Spacer(1, 6))

    # ----- 3. Application Architecture -----
    h1("3. Application Architecture")
    p("The app uses a Flask application factory pattern. Entry point is <b>run.py</b>, which creates the app via <b>create_app()</b> in <b>app/__init__.py</b>. Configuration is in <b>app/config.py</b> (database path, secret key, upload folders).")
    h2("Blueprint Modules")
    p("• <b>auth</b> – Login and logout; redirects to role-specific dashboard after login.<br/>• <b>main</b> – Home, timetable view, staff directory (shared).<br/>• <b>student</b> – Student dashboard, attendance, fees, leave application, notes, certificates.<br/>• <b>faculty</b> – Faculty dashboard, mark attendance, upload/manage notes.<br/>• <b>admin</b> – Admin dashboard, user/student management, leave approval, certificate upload, timetable and staff management.")
    h2("Data Flow")
    p("User logs in → Flask-Login authenticates → role is checked → user is redirected to the correct dashboard. All subsequent requests use the same session. Routes load data via SQLAlchemy models, render Jinja2 templates, and return HTML. File uploads (notes, certificates) are validated and stored under <b>static/uploads/</b>.")
    story.append(Spacer(1, 6))

    # ----- 4. Database Models -----
    h1("4. Database Models")
    p("All models are defined in <b>app/models.py</b> and use Flask-SQLAlchemy.")
    data = [
        ["Model", "Purpose"],
        ["User", "Central account: username, email, password_hash, role (admin/faculty/student), is_active."],
        ["Department", "Departments (e.g. CS, EC) with code, head, contact."],
        ["Course", "Courses linked to department and semester; optional faculty, room, schedule."],
        ["Enrollment", "Student–course enrollment with grade/marks and status."],
        ["Student", "Links to User; roll_no, department_id, semester, phone, address."],
        ["Faculty", "Links to User; designation, department, phone, office."],
        ["Attendance", "Per-student, per-date status (present/absent/leave); marked_by user."],
        ["Leave", "Applications: user_id, start/end date, reason, status (pending/approved/rejected), resolved_by."],
        ["Fee", "Per student per semester: amount, status, due_date, paid_date."],
        ["Note", "Study materials: faculty user_id, title, subject, file_path, department, semester."],
        ["Certificate", "Admin-uploaded; student_id, certificate_type, file_path, issue_date."],
        ["Timetable", "Department, semester, day, time, subject, faculty_name, room_no."],
        ["Staff", "Non-faculty staff: name, designation, department, email, phone, office."],
    ]
    t = Table(data, colWidths=[1.2*inch, 4.3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # ----- 5. Authentication & Security -----
    h1("5. Authentication &amp; Security")
    p("• Passwords are hashed with Werkzeug; never stored in plain text.<br/>• Flask-Login manages sessions and the <b>current_user</b> object.<br/>• Routes that require login use the <b>@login_required</b> decorator.<br/>• Role checks (e.g. admin-only) are done in routes or templates.<br/>• SQLAlchemy ORM prevents SQL injection.<br/>• File uploads: allowed types (e.g. PDF, DOC, images) and secure filenames (e.g. UUID-based) are enforced in <b>app/utils/file_handler.py</b>.")
    story.append(Spacer(1, 6))

    # ----- 6. How It Works by Role -----
    h1("6. How It Works by Role")
    h2("Student")
    p("Students log in and see a dashboard with quick stats (attendance, fees, certificates). They can view attendance history, fee status per semester, apply for leave (dates + reason), track leave status, download study notes filtered by department/semester, download certificates, and view timetable and staff directory.")
    h2("Faculty")
    p("Faculty see a department-focused dashboard. They can mark attendance in bulk for a selected date (present/absent/leave), upload study materials (file + title, subject, department, semester), manage or delete their uploaded notes, view student lists, and access the timetable.")
    h2("Admin")
    p("Admins get a system overview dashboard. They can view and filter users by role, manage student records (e.g. by department), approve or reject leave applications, upload certificates for students, manage timetable entries, manage the staff directory (add/remove staff), and see system statistics.")
    story.append(Spacer(1, 6))

    # ----- 7. Key Workflows -----
    h1("7. Key Workflows")
    h2("Leave Application Flow")
    p("1. Student submits leave (Apply for Leave) with start date, end date, and reason.<br/>2. Leave is stored with status &quot;Pending&quot;.<br/>3. Admin sees pending leaves in Manage Leaves.<br/>4. Admin approves or rejects; status and optional remarks are updated.<br/>5. Student sees updated status under My Leaves.")
    h2("Attendance Flow")
    p("1. Faculty opens Mark Attendance and selects a date.<br/>2. System lists students (e.g. by department/course).<br/>3. Faculty sets each student as Present, Absent, or Leave and saves.<br/>4. Records are stored with student_id, date, status, and marked_by.<br/>5. Students view their attendance on the View Attendance page.")
    h2("Notes &amp; Certificates")
    p("Notes: Faculty upload a file; it is saved under static/uploads/notes/ and linked in the Note model. Students view notes filtered by department/semester and download from the same path.<br/><br/>Certificates: Admin upload a file for a student; it is saved under static/uploads/certificates/ and linked in the Certificate model. Students see and download their assigned certificates.")
    story.append(Spacer(1, 6))

    # ----- 8. Project Structure -----
    h1("8. Project Structure")
    p("• <b>run.py</b> – Entry point; creates app and runs server (e.g. port 5500).<br/>• <b>app/</b> – Flask package: __init__.py (factory, blueprints, db, default users), config.py, models.py; subpackages auth, main, student, faculty, admin, utils.<br/>• <b>templates/</b> – Jinja2 templates: base, auth, dashboard, attendance, leave, fees, notes, certificates, timetable, staff, admin.<br/>• <b>static/</b> – css, js, uploads (notes, certificates).<br/>• <b>scripts/</b> – init_db, create_admin, seed_data, clear_attendance, etc.<br/>• <b>data/</b> – SQLite database file (erp_system.db).<br/>• <b>docs/</b> – Markdown documentation.")
    story.append(Spacer(1, 6))

    # ----- 9. Running the Project -----
    h1("9. Running the Project")
    p("Install dependencies: <b>pip install -r requirements.txt</b><br/>Start the app: <b>python run.py</b><br/>Open in browser: <b>http://localhost:5500</b> (or the port shown in run.py).")
    p("Optional: Initialize or reset DB with <b>python scripts/init_db.py</b>; add sample data with <b>python scripts/seed_data.py</b>; create an admin with <b>python scripts/create_admin.py</b>.")
    h2("Default Demo Accounts")
    data2 = [
        ["Role", "Username", "Password"],
        ["Admin", "admin", "admin123"],
        ["Faculty", "faculty", "faculty123"],
        ["Student", "student", "student123"],
    ]
    t2 = Table(data2, colWidths=[1.2*inch, 1.5*inch, 1.5*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # ----- 10. Summary -----
    h1("10. Summary")
    p("LumenERP is a complete college ERP with role-based access, secure authentication, and modules for attendance, fees, leave, notes, certificates, timetable, and staff. The working of the project is driven by Flask blueprints, SQLAlchemy models, and Jinja2 templates; users interact through their role-specific dashboards and the workflows described above.")
    story.append(Spacer(1, 12))
    p("— End of document —", ParagraphStyle(name='End', parent=styles['Normal'], fontSize=9, textColor=colors.grey))

    doc.build(story)
    return output_path


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    output_path = os.path.join(docs_dir, 'LumenERP_Project_Working.pdf')
    build_pdf(output_path)
    print(f"PDF created successfully: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
