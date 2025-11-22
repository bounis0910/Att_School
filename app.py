import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
from io import BytesIO
from openpyxl import Workbook, load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


### Models (simple definitions here) ###
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, staff, teacher, student
    password_hash = db.Column(db.String(200), nullable=True)
    # For staff/teacher linking, simple comma-separated class ids (quick implementation)
    classes = db.Column(db.String(200), nullable=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, pw)


class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))
    klass = db.relationship('SchoolClass')


class TeacherSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    date = db.Column(db.String(20), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present/absent
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.cli.command('init-db')
def init_db():
    db.create_all()
    # create default admin if not exists
    if not User.query.filter_by(role='admin').first():
        admin = User(name='Administrator', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print('Created default admin (username: Administrator, password: admin)')


### Routes ###
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form['name']
        pw = request.form['password']
        user = User.query.filter_by(name=name, role='admin').first()
        if user and user.check_password(pw):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')


@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        name = request.form['name']
        pw = request.form['password']
        user = User.query.filter_by(name=name, role='staff').first()
        if user and user.check_password(pw):
            login_user(user)
            return redirect(url_for('staff_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('staff_login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    classes = SchoolClass.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', classes=classes, teachers=teachers, subjects=subjects)


@app.route('/admin/import', methods=['GET', 'POST'])
@login_required
def admin_import():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash('No file uploaded', 'warning')
            return redirect(request.url)
        df = pd.read_excel(f, sheet_name=None)
        # Expect sheets: students, teachers, classes, subjects
        if 'classes' in df:
            for _, row in df['classes'].iterrows():
                name = str(row.get('name') or row.get('class') or row.get('Class') or '').strip()
                if name:
                    if not SchoolClass.query.filter_by(name=name).first():
                        db.session.add(SchoolClass(name=name))
        if 'students' in df:
            for _, row in df['students'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                class_name = str(row.get('class') or row.get('Class') or '').strip()
                if name:
                    klass = SchoolClass.query.filter_by(name=class_name).first() if class_name else None
                    s = Student(name=name, class_id=klass.id if klass else None)
                    db.session.add(s)
        if 'teachers' in df:
            for _, row in df['teachers'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                if name:
                    if not User.query.filter_by(name=name, role='teacher').first():
                        t = User(name=name, role='teacher')
                        db.session.add(t)
        if 'subjects' in df:
            for _, row in df['subjects'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                if name and not Subject.query.filter_by(name=name).first():
                    db.session.add(Subject(name=name))
        db.session.commit()
        flash('Import completed', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('import.html')


@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    teachers = User.query.filter_by(role='teacher').all()
    classes = SchoolClass.query.all()
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        class_id = request.form.get('class_id')
        if not teacher_id or not class_id:
            flash('Select teacher and class', 'warning')
            return redirect(request.url)
        session['teacher_id'] = int(teacher_id)
        session['class_id'] = int(class_id)
        return redirect(url_for('teacher_dashboard'))
    return render_template('teacher_login.html', teachers=teachers, classes=classes)


@app.route('/teacher/dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    teacher_id = session.get('teacher_id')
    class_id = session.get('class_id')
    if not teacher_id or not class_id:
        return redirect(url_for('teacher_login'))
    teacher = User.query.get(teacher_id)
    klass = SchoolClass.query.get(class_id)
    students = Student.query.filter_by(class_id=class_id).all()
    today = date.today().isoformat()
    if request.method == 'POST':
        # form contains period and statuses list
        period = int(request.form.get('period') or 1)
        for student in students:
            status = request.form.get(f'status_{student.id}', 'present')
            att = Attendance.query.filter_by(student_id=student.id, date=today, period=period).first()
            if att:
                att.status = status
            else:
                att = Attendance(student_id=student.id, date=today, period=period, status=status, class_id=class_id, teacher_id=teacher_id)
                db.session.add(att)
        db.session.commit()
        # update daily Excel file
        update_daily_excel(today)
        flash('Attendance saved', 'success')
        return redirect(url_for('teacher_dashboard'))

    # build attendance map
    attendance = {}
    records = Attendance.query.filter_by(date=today, class_id=class_id).all()
    for r in records:
        attendance.setdefault(r.period, {})[r.student_id] = r.status

    return render_template('teacher_dashboard.html', teacher=teacher, klass=klass, students=students, attendance=attendance, today=today)


def update_daily_excel(today_str):
    # create or update a workbook per date
    export_dir = os.path.join(basedir, 'exports')
    os.makedirs(export_dir, exist_ok=True)
    fname = os.path.join(export_dir, f'attendance-{today_str}.xlsx')
    if os.path.exists(fname):
        wb = load_workbook(fname)
    else:
        wb = Workbook()
        # remove default sheet
        if 'Sheet' in wb.sheetnames:
            std = wb['Sheet']
            wb.remove(std)

    classes = SchoolClass.query.all()
    for klass in classes:
        sheet_name = klass.name[:31]
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.create_sheet(sheet_name)
            ws.sheet_view.rightToLeft = True
        # first two rows: date+class, then headers
        ws.delete_rows(1, ws.max_row)
        ws.append([f'Date: {today_str}  Class: {klass.name}'])
        # header row: names and periods placeholder
        students = Student.query.filter_by(class_id=klass.id).all()
        header = ['Student'] + [f'P{i+1}' for i in range(8)]
        ws.append(header)
        for s in students:
            row = [s.name] + ['' for _ in range(len(header)-1)]
            # fill from db
            for i in range(1, len(header)):
                att = Attendance.query.filter_by(student_id=s.id, date=today_str, period=i, class_id=klass.id).first()
                if att:
                    row[i] = 'A' if att.status == 'absent' else 'P'
            ws.append(row)

    wb.save(fname)


@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    today = date.today().isoformat()
    classes = SchoolClass.query.all()
    summary = []
    for klass in classes:
        students = Student.query.filter_by(class_id=klass.id).all()
        total = len(students)
        absences = Attendance.query.filter_by(date=today, class_id=klass.id, status='absent').count()
        summary.append({'class': klass, 'total': total, 'absences': absences})
    return render_template('staff_dashboard.html', summary=summary, today=today)


@app.route('/staff/export_excel')
@login_required
def staff_export_excel():
    if current_user.role != 'staff':
        return redirect(url_for('index'))
    today = date.today().isoformat()
    fname = os.path.join(basedir, 'exports', f'attendance-{today}.xlsx')
    if not os.path.exists(fname):
        flash('No attendance file for today', 'warning')
        return redirect(url_for('staff_dashboard'))
    return send_file(fname, as_attachment=True)


@app.route('/admin/export_pdf')
@login_required
def admin_export_pdf():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    today = date.today().isoformat()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    classes = SchoolClass.query.all()
    for klass in classes:
        elements.append(Paragraph(f'Class: {klass.name} - Date: {today}', styles['Heading3']))
        students = Student.query.filter_by(class_id=klass.id).all()
        data = [['Student', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']]
        for s in students:
            row = [s.name]
            for p in range(1,9):
                att = Attendance.query.filter_by(student_id=s.id, date=today, period=p, class_id=klass.id).first()
                row.append('A' if att and att.status=='absent' else 'P' if att else '')
            data.append(row)
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, download_name=f'attendance-{today}.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
