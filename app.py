import os
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import click
from flask_migrate import Migrate

import pandas as pd
from io import BytesIO
from openpyxl import Workbook, load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import or_, text
import re

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


### Models (simple definitions here) ###
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, staff, teacher, student
    password_hash = db.Column(db.String(200), nullable=True)
    national_id = db.Column(db.String(50), nullable=True)
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
    national_id = db.Column(db.String(50), nullable=True)


class TeacherSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 0 = Monday .. 6 = Sunday
    day_of_week = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(8), nullable=True)  # HH:MM
    end_time = db.Column(db.String(8), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    klass = db.relationship('SchoolClass', foreign_keys=[class_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    __table_args__ = (
        db.UniqueConstraint('day_of_week', 'period', 'class_id', name='uq_period_day_period_class'),
    )


def get_current_period_for_class(class_id=None):
    """Return current period number for today for given class_id or global (None).
    Looks for Period entries whose time range includes now. Returns (period_number, Period) or (None, None).
    """
    weekday = date.today().weekday()
    periods_today = Period.query.filter(Period.day_of_week == weekday).filter(
        or_(Period.class_id == None, Period.class_id == class_id) if class_id is None else
        or_(Period.class_id == None, Period.class_id == class_id)
    ).order_by(Period.period).all()
    now = datetime.now().time()
    def parse_t(tstr):
        try:
            return datetime.strptime(tstr, '%H:%M').time()
        except Exception:
            return None
    for p in periods_today:
        st = parse_t(p.start_time) if p.start_time else None
        en = parse_t(p.end_time) if p.end_time else None
        if st and en and st <= now <= en:
            return p.period, p
    return None, None


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    date = db.Column(db.String(20), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present/absent
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student = db.relationship('Student', backref='attendances', foreign_keys=[student_id])
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    klass = db.relationship('SchoolClass', foreign_keys=[class_id])


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


@app.cli.command('add-teacher')
@click.argument('name')
@click.option('--password', default=None, help='Optional password for the teacher')
@click.option('--nid', default=None, help='Optional national id for the teacher')
def add_teacher(name, password, nid):
    """Add a teacher user to the database: flask --app app add-teacher "Name" --password pw"""
    if User.query.filter_by(name=name, role='teacher').first():
        print(f'Teacher "{name}" already exists')
        return
    t = User(name=name, role='teacher')
    if password:
        t.set_password(password)
    if nid:
        t.national_id = nid
    db.session.add(t)
    db.session.commit()
    print(f'Added teacher: {name}')


@app.cli.command('import-teachers')
@click.argument('path')
def import_teachers(path):
    """Import teachers from an Excel file. Use sheet named 'teachers' or first sheet."""
    if not os.path.exists(path):
        print('File not found:', path)
        return
    try:
        sheets = pd.read_excel(path, sheet_name=None)
    except Exception as e:
        print('Failed to read Excel:', e)
        return
    # try 'teachers' sheet first
    df = None
    if 'teachers' in sheets:
        df = sheets['teachers']
    else:
        # take first sheet
        df = next(iter(sheets.values()))
    added = 0
    for _, row in df.iterrows():
        name = str(row.get('name') or row.get('Name') or '').strip()
        if not name:
            continue
        if User.query.filter_by(name=name, role='teacher').first():
            continue
        t = User(name=name, role='teacher')
        # try common national id column names
        nid = row.get('national_id') or row.get('national id') or row.get('nid') or row.get('NationalID') or row.get('NID')
        if nid is not None:
            t.national_id = str(nid).strip()
        db.session.add(t)
        added += 1
    db.session.commit()
    print(f'Imported {added} teachers from {path}')


@app.cli.command('add-student')
@click.argument('name')
@click.option('--class', 'class_name', default=None, help='Class name to assign')
@click.option('--nid', default=None, help='Optional national id for the student')
def add_student(name, class_name, nid):
    """Add a student: flask --app app add-student "Name" --class "Class name" --nid 12345"""
    klass = None
    if class_name:
        klass = SchoolClass.query.filter_by(name=class_name).first()
        if not klass:
            klass = SchoolClass(name=class_name)
            db.session.add(klass)
            db.session.commit()
    s = Student(name=name, class_id=klass.id if klass else None)
    if nid:
        s.national_id = nid
    db.session.add(s)
    db.session.commit()
    print(f'Added student: {name}')


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
    # compute global current period (no specific class)
    current_period, _ = get_current_period_for_class(None)
    # compute per-class current period map
    class_current = {c.id: get_current_period_for_class(c.id)[0] for c in classes}
    return render_template('admin_dashboard.html', classes=classes, teachers=teachers, subjects=subjects, current_period=current_period, class_current=class_current)


### Admin CRUD: Users / Classes / Subjects / Students / Attendance ###


def admin_required():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return False
    return True


@app.route('/admin/users')
@login_required
def admin_users():
    if not admin_required():
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_users_create():
    if not admin_required():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        password = request.form.get('password') or None
        nid = request.form.get('national_id') or None
        u = User(name=name, role=role)
        if password:
            u.set_password(password)
        if nid:
            u.national_id = nid
        db.session.add(u)
        db.session.commit()
        flash('User created', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', user=None)


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_users_edit(user_id):
    if not admin_required():
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.role = request.form['role']
        pw = request.form.get('password')
        if pw:
            user.set_password(pw)
        user.national_id = request.form.get('national_id') or None
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', user=user)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    if not admin_required():
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/classes')
@login_required
def admin_classes():
    if not admin_required():
        return redirect(url_for('index'))
    classes = SchoolClass.query.all()
    return render_template('admin_classes.html', classes=classes)


@app.route('/admin/classes/create', methods=['GET', 'POST'])
@login_required
def admin_classes_create():
    if not admin_required():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        c = SchoolClass(name=name)
        db.session.add(c)
        db.session.commit()
        flash('Class created', 'success')
        return redirect(url_for('admin_classes'))
    return render_template('admin_class_form.html', klass=None)


@app.route('/admin/classes/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_classes_edit(class_id):
    if not admin_required():
        return redirect(url_for('index'))
    klass = SchoolClass.query.get_or_404(class_id)
    if request.method == 'POST':
        klass.name = request.form['name']
        db.session.commit()
        flash('Class updated', 'success')
        return redirect(url_for('admin_classes'))
    return render_template('admin_class_form.html', klass=klass)


@app.route('/admin/classes/<int:class_id>/delete', methods=['POST'])
@login_required
def admin_classes_delete(class_id):
    if not admin_required():
        return redirect(url_for('index'))
    klass = SchoolClass.query.get_or_404(class_id)
    db.session.delete(klass)
    db.session.commit()
    flash('Class deleted', 'success')
    return redirect(url_for('admin_classes'))


@app.route('/admin/subjects')
@login_required
def admin_subjects():
    if not admin_required():
        return redirect(url_for('index'))
    subjects = Subject.query.all()
    return render_template('admin_subjects.html', subjects=subjects)


@app.route('/admin/subjects/create', methods=['GET', 'POST'])
@login_required
def admin_subjects_create():
    if not admin_required():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        s = Subject(name=name)
        db.session.add(s)
        db.session.commit()
        flash('Subject created', 'success')
        return redirect(url_for('admin_subjects'))
    return render_template('admin_subject_form.html', subject=None)


@app.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_subjects_edit(subject_id):
    if not admin_required():
        return redirect(url_for('index'))
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form['name']
        db.session.commit()
        flash('Subject updated', 'success')
        return redirect(url_for('admin_subjects'))
    return render_template('admin_subject_form.html', subject=subject)


@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def admin_subjects_delete(subject_id):
    if not admin_required():
        return redirect(url_for('index'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted', 'success')
    return redirect(url_for('admin_subjects'))


### Admin: Periods (schedule) ###
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@app.route('/admin/periods')
@login_required
def admin_periods():
    if not admin_required():
        return redirect(url_for('index'))
    periods = Period.query.order_by(Period.day_of_week, Period.period).all()
    classes = SchoolClass.query.all()
    subjects = Subject.query.all()
    return render_template('admin_periods.html', periods=periods, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/create', methods=['GET', 'POST'])
@login_required
def admin_periods_create():
    if not admin_required():
        return redirect(url_for('index'))
    classes = SchoolClass.query.all()
    subjects = Subject.query.all()
    if request.method == 'POST':
        day = int(request.form.get('day_of_week'))
        period_no = int(request.form.get('period'))
        start_time = request.form.get('start_time') or None
        end_time = request.form.get('end_time') or None
        class_id = request.form.get('class_id') or None
        subject_id = request.form.get('subject_id') or None
        # validation: prevent duplicate day+period for same class (or global None)
        existing = Period.query.filter_by(day_of_week=day, period=period_no, class_id=class_id if class_id else None).first()
        if existing:
            flash('A period with the same day/number and class already exists', 'warning')
            return redirect(url_for('admin_periods'))
        p = Period(day_of_week=day, period=period_no, start_time=start_time, end_time=end_time,
                   class_id=class_id if class_id else None, subject_id=subject_id if subject_id else None)
        db.session.add(p)
        db.session.commit()
        flash('Period created', 'success')
        return redirect(url_for('admin_periods'))
    return render_template('admin_period_form.html', period=None, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_periods_edit(period_id):
    if not admin_required():
        return redirect(url_for('index'))
    p = Period.query.get_or_404(period_id)
    classes = SchoolClass.query.all()
    subjects = Subject.query.all()
    if request.method == 'POST':
        new_day = int(request.form.get('day_of_week'))
        new_period = int(request.form.get('period'))
        new_start = request.form.get('start_time') or None
        new_end = request.form.get('end_time') or None
        new_class_id = request.form.get('class_id') or None
        new_subject_id = request.form.get('subject_id') or None
        # check duplicates excluding current record
        existing = Period.query.filter_by(day_of_week=new_day, period=new_period, class_id=new_class_id if new_class_id else None).first()
        if existing and existing.id != p.id:
            flash('Another period with same day/number and class exists', 'warning')
            return redirect(url_for('admin_periods'))
        p.day_of_week = new_day
        p.period = new_period
        p.start_time = new_start
        p.end_time = new_end
        p.class_id = new_class_id or None
        p.subject_id = new_subject_id or None
        db.session.commit()
        flash('Period updated', 'success')
        return redirect(url_for('admin_periods'))
    return render_template('admin_period_form.html', period=p, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/<int:period_id>/delete', methods=['POST'])
@login_required
def admin_periods_delete(period_id):
    if not admin_required():
        return redirect(url_for('index'))
    p = Period.query.get_or_404(period_id)
    db.session.delete(p)
    db.session.commit()
    flash('Period deleted', 'success')
    return redirect(url_for('admin_periods'))


@app.cli.command('apply-unique-index')
def apply_unique_index():
    """Apply unique index for Period (safe for SQLite)."""
    # create unique index if not exists (SQLite supports IF NOT EXISTS)
    try:
        sql = "CREATE UNIQUE INDEX IF NOT EXISTS uq_period_day_period_class_idx ON period (day_of_week, period, class_id);"
        with db.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print('Unique index applied (if it did not already exist).')
    except Exception as e:
        print('Failed to apply unique index:', e)


@app.route('/admin/students')
@login_required
def admin_students():
    if not admin_required():
        return redirect(url_for('index'))
    students = Student.query.all()
    classes = SchoolClass.query.all()
    return render_template('admin_students.html', students=students, classes=classes)


@app.route('/admin/students/create', methods=['GET', 'POST'])
@login_required
def admin_students_create():
    if not admin_required():
        return redirect(url_for('index'))
    classes = SchoolClass.query.all()
    if request.method == 'POST':
        name = request.form['name']
        class_id = request.form.get('class_id') or None
        nid = request.form.get('national_id') or None
        s = Student(name=name, class_id=class_id)
        if nid:
            s.national_id = nid
        db.session.add(s)
        db.session.commit()
        flash('Student created', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin_student_form.html', student=None, classes=classes)


@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_students_edit(student_id):
    if not admin_required():
        return redirect(url_for('index'))
    student = Student.query.get_or_404(student_id)
    classes = SchoolClass.query.all()
    if request.method == 'POST':
        student.name = request.form['name']
        student.class_id = request.form.get('class_id') or None
        student.national_id = request.form.get('national_id') or None
        db.session.commit()
        flash('Student updated', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin_student_form.html', student=student, classes=classes)


@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
def admin_students_delete(student_id):
    if not admin_required():
        return redirect(url_for('index'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/attendance')
@login_required
def admin_attendance():
    if not admin_required():
        return redirect(url_for('index'))
    today = request.args.get('date') or date.today().isoformat()
    records = Attendance.query.filter_by(date=today).all()
    return render_template('admin_attendance.html', records=records, today=today)


@app.route('/admin/attendance/<int:att_id>/delete', methods=['POST'])
@login_required
def admin_attendance_delete(att_id):
    if not admin_required():
        return redirect(url_for('index'))
    att = Attendance.query.get_or_404(att_id)
    db.session.delete(att)
    db.session.commit()
    flash('Attendance record deleted', 'success')
    return redirect(url_for('admin_attendance'))


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
                # try common national id column names
                nid = row.get('national_id') or row.get('national id') or row.get('nid') or row.get('NationalID') or row.get('NID')
                if name:
                    klass = SchoolClass.query.filter_by(name=class_name).first() if class_name else None
                    s = Student(name=name, class_id=klass.id if klass else None)
                    if nid is not None:
                        s.national_id = str(nid).strip()
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
    # compute today's periods for this class and current period based on time
    weekday = date.today().weekday()
    periods_today = Period.query.filter(Period.day_of_week == weekday).filter(or_(Period.class_id == None, Period.class_id == class_id)).order_by(Period.period).all()
    current_period = None
    now = datetime.now().time()
    def parse_t(tstr):
        try:
            return datetime.strptime(tstr, '%H:%M').time()
        except Exception:
            return None
    for p in periods_today:
        st = parse_t(p.start_time) if p.start_time else None
        en = parse_t(p.end_time) if p.end_time else None
        if st and en and st <= now <= en:
            current_period = p.period
            break
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

    return render_template('teacher_dashboard.html', teacher=teacher, klass=klass, students=students, attendance=attendance, today=today, periods_today=periods_today, current_period=current_period)


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

    def get_safe_sheet_name(wb, name):
        # invalid chars for Excel sheet names: : \ / ? * [ ]
        invalid_re = r"[:\\\\/?*\[\]]"
        base = re.sub(invalid_re, '-', name)
        base = base.strip()[:31] or 'Sheet'
        candidate = base
        i = 1
        while candidate in wb.sheetnames:
            suffix = f'_{i}'
            max_base_len = 31 - len(suffix)
            candidate = (base[:max_base_len]).rstrip() + suffix
            i += 1
        return candidate

    classes = SchoolClass.query.all()
    for klass in classes:
        safe_name = get_safe_sheet_name(wb, klass.name)
        if safe_name in wb.sheetnames:
            ws = wb[safe_name]
        else:
            ws = wb.create_sheet(safe_name)
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
        class_cp = get_current_period_for_class(klass.id)[0]
        summary.append({'class': klass, 'total': total, 'absences': absences, 'current_period': class_cp})
    # global current period
    current_period, _ = get_current_period_for_class(None)
    return render_template('staff_dashboard.html', summary=summary, today=today, current_period=current_period)


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
