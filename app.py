import os
from datetime import date, datetime
import pytz

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import click
from flask_migrate import Migrate
import sqlite3
from flask import g

import pandas as pd
from io import BytesIO
from openpyxl import Workbook, load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import or_, text
import re
from openpyxl.styles import Font, PatternFill, Alignment

basedir = os.path.abspath(os.path.dirname(__file__))

# Timezone configuration
TIMEZONE = pytz.timezone('Asia/Qatar')  # Change this to your timezone

def get_current_datetime():
    """Get current datetime with timezone."""
    return datetime.now(TIMEZONE)

def get_current_date():
    """Get current date with timezone."""
    return get_current_datetime().date()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

migrate = None
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Lightweight db stub: keep legacy SQLAlchemy model definitions import-safe
# Model classes remain in the file for reference only; runtime DB access uses sqlite3 helpers.
class _DBStub:
    class Model:
        pass
    def Column(self, *args, **kwargs):
        return None
    Integer = int
    def String(self, *args, **kwargs):
        return str
    def ForeignKey(self, *args, **kwargs):
        return None
    def UniqueConstraint(self, *args, **kwargs):
        return None
    def relationship(self, *args, **kwargs):
        return None

db = _DBStub()

# SQLite helper (parallel, for a lightweight DB layer)
DATABASE = os.path.join(basedir, 'app.db')

def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        db_conn.row_factory = sqlite3.Row
        g._database = db_conn
    return db_conn


@app.teardown_appcontext
def close_db(exc):
    db_conn = getattr(g, '_database', None)
    if db_conn is not None:
        db_conn.close()


class RowObject:
    """Wrap sqlite3.Row to allow attribute access used by templates."""
    def __init__(self, row):
        self._r = row
    def __getattr__(self, name):
        try:
            return self._r[name]
        except Exception:
            raise AttributeError(name)


class SimpleUser(UserMixin):
    """Lightweight user adapter for Flask-Login backed by sqlite rows."""
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.role = row['role']
        self.password_hash = row['password_hash'] if 'password_hash' in row.keys() else None

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)
    def check_password(self, pw):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, pw)


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
    Uses sqlite `period` table. Returns (period_number, row) or (None, None).
    """
    weekday = get_current_date().weekday()
    conn = get_db()
    if class_id is None:
        rows = conn.execute(
            "SELECT * FROM period WHERE day_of_week = ? AND class_id IS NULL ORDER BY period",
            (weekday,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM period WHERE day_of_week = ? AND (class_id IS NULL OR class_id = ?) ORDER BY period",
            (weekday, class_id),
        ).fetchall()

    now = get_current_datetime().time()

    def parse_t(tstr):
        try:
            return datetime.strptime(tstr, '%H:%M').time()
        except Exception:
            return None

    for r in rows:
        st = parse_t(r['start_time']) if r['start_time'] else None
        en = parse_t(r['end_time']) if r['end_time'] else None
        if st and en and st <= now <= en:
            return r['period'], r
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
    conn = get_db()
    row = conn.execute("SELECT * FROM user WHERE id = ?", (int(user_id),)).fetchone()
    return SimpleUser(row) if row else None


@app.cli.command('init-db')
def init_db():
    """Initialize DB tables using sqlite3 (safe to call multiple times)."""
    conn = get_db()
    cur = conn.cursor()
    # create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        password_hash TEXT,
        national_id TEXT,
        classes TEXT,
        email TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS school_class (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class_id INTEGER,
        national_id TEXT,
        FOREIGN KEY(class_id) REFERENCES school_class(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS period (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week INTEGER NOT NULL,
        period INTEGER NOT NULL,
        start_time TEXT,
        end_time TEXT,
        class_id INTEGER,
        subject_id INTEGER,
        UNIQUE(day_of_week, period, class_id),
        FOREIGN KEY(class_id) REFERENCES school_class(id),
        FOREIGN KEY(subject_id) REFERENCES subject(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT NOT NULL,
        period INTEGER NOT NULL,
        status TEXT NOT NULL,
        class_id INTEGER,
        teacher_id INTEGER,
        remark TEXT,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT,
        UNIQUE(student_id, date, period),
        FOREIGN KEY(student_id) REFERENCES student(id),
        FOREIGN KEY(class_id) REFERENCES school_class(id),
        FOREIGN KEY(teacher_id) REFERENCES user(id)
    );
    """)
    conn.commit()

    # create default admin if not exists
    r = conn.execute("SELECT id FROM user WHERE role = ? LIMIT 1", ('admin',)).fetchone()
    if not r:
        pw = generate_password_hash('admin')
        conn.execute("INSERT INTO user (name, role, password_hash) VALUES (?,?,?)",
                     ('Administrator', 'admin', pw))
        conn.commit()
        print('Created default admin (username: Administrator, password: admin)')
    else:
        print('DB initialized')

    # Ensure `email` column exists on `user` table for teacher email/password login
    try:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(user)").fetchall()]
        if 'email' not in cols:
            conn.execute("ALTER TABLE user ADD COLUMN email TEXT")
            conn.commit()
            print('Added `email` column to user table')
    except Exception:
        # non-fatal: schema migration best-effort
        pass


@app.cli.command('add-teacher')
@click.argument('name')
@click.option('--password', default=None, help='Optional password for the teacher')
@click.option('--nid', default=None, help='Optional national id for the teacher')
@click.option('--ph1', default=None, help='Optional national id for the teacher')
def add_teacher(name, password, nid):
    """Add a teacher user to the database: flask --app app add-teacher "Name" --password pw"""
    conn = get_db()
    # check exists
    exists = conn.execute("SELECT id FROM user WHERE name = ? AND role = ?", (name, 'teacher')).fetchone()
    if exists:
        print(f'Teacher "{name}" already exists')
        return
    pw_hash = generate_password_hash(password) if password else None
    conn.execute("INSERT INTO user (name, role, password_hash, national_id) VALUES (?,?,?,?)",
                 (name, 'teacher', pw_hash, nid))
    conn.commit()
    print(f'Added teacher: {name}')


@app.cli.command('set-teacher-email')
@click.argument('name')
@click.argument('email')
def set_teacher_email(name, email):
    """Set or update email for a teacher: flask --app app set-teacher-email "Name" email@example.com"""
    conn = get_db()
    teacher = conn.execute("SELECT id FROM user WHERE name = ? AND role = ?", (name, 'teacher')).fetchone()
    if not teacher:
        print(f'Teacher "{name}" not found')
        return
    conn.execute("UPDATE user SET email = ? WHERE id = ?", (email, teacher['id']))
    conn.commit()
    print(f'Updated email for teacher "{name}" to {email}')


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
    conn = get_db()
    added = 0
    for _, row in df.iterrows():
        name = str(row.get('name') or row.get('Name') or '').strip()
        if not name:
            continue
        exists = conn.execute("SELECT id FROM user WHERE name = ? AND role = ?", (name, 'teacher')).fetchone()
        if exists:
            continue
        nid = row.get('national_id') or row.get('national id') or row.get('nid') or row.get('NationalID') or row.get('NID')
        conn.execute("INSERT INTO user (name, role, national_id) VALUES (?,?,?)", (name, 'teacher', str(nid).strip() if nid is not None else None))
        added += 1
    conn.commit()
    print(f'Imported {added} teachers from {path}')


@app.cli.command('add-student')
@click.argument('name')
@click.option('--class', 'class_name', default=None, help='Class name to assign')
@click.option('--nid', default=None, help='Optional national id for the student')
def add_student(name, class_name, nid):
    """Add a student: flask --app app add-student "Name" --class "Class name" --nid 12345"""
    conn = get_db()
    class_id = None
    if class_name:
        c = conn.execute("SELECT id FROM school_class WHERE name = ?", (class_name,)).fetchone()
        if c:
            class_id = c['id']
        else:
            res = conn.execute("INSERT INTO school_class (name) VALUES (?)", (class_name,))
            conn.commit()
            class_id = conn.execute("SELECT id FROM school_class WHERE name = ?", (class_name,)).fetchone()['id']
    conn.execute("INSERT INTO student (name, class_id, national_id) VALUES (?,?,?)", (name, class_id, nid))
    conn.commit()
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
        conn = get_db()
        row = conn.execute("SELECT * FROM user WHERE name = ? AND role = ? LIMIT 1", (name, 'admin')).fetchone()
        if row:
            user = SimpleUser(row)
            if user.check_password(pw):
                login_user(user)
                return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')


@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['password']
        conn = get_db()
        row = conn.execute("SELECT * FROM user WHERE email = ? AND role = ? LIMIT 1", (email, 'staff')).fetchone()
        if row:
            user = SimpleUser(row)
            if user.check_password(pw):
                login_user(user)
                return redirect(url_for('staff_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('staff_login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow users to change their own password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        conn = get_db()
        user_id = int(current_user.get_id())
        row = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        
        if not row:
            flash('User not found', 'danger')
            return redirect(url_for('index'))
        
        user = SimpleUser(row)
        
        # Validate current password
        if not user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('change_password.html')
        
        # Validate new password
        if not new_password:
            flash('New password is required', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        elif len(new_password) < 4:
            flash('Password must be at least 4 characters', 'danger')
        else:
            # Update password
            pw_hash = generate_password_hash(new_password)
            conn.execute("UPDATE user SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
            conn.commit()
            flash('Password changed successfully', 'success')
            
            # Redirect based on role
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            elif current_user.role == 'teacher':
                return redirect(url_for('teacher_classes'))
            else:
                return redirect(url_for('index'))
    
    return render_template('change_password.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db()
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    teachers_rows = conn.execute("SELECT * FROM user WHERE role = ? ORDER BY name", ('teacher',)).fetchall()
    teachers = [RowObject(r) for r in teachers_rows]
    subjects_rows = conn.execute("SELECT * FROM subject ORDER BY name").fetchall()
    subjects = [RowObject(r) for r in subjects_rows]
    # compute global current period (no specific class)
    current_period, _ = get_current_period_for_class(None)
    # compute per-class current period map
    class_current = {c.id: (get_current_period_for_class(c.id)[0] if get_current_period_for_class(c.id)[0] is not None else None) for c in classes}
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
    conn = get_db()
    rows = conn.execute("SELECT * FROM user ORDER BY name").fetchall()
    users = [RowObject(r) for r in rows]
    
    # Fetch all classes for lookup
    classes_rows = conn.execute("SELECT * FROM school_class").fetchall()
    classes_dict = {str(r['id']): r['name'] for r in classes_rows}
    
    return render_template('admin_users.html', users=users, classes_dict=classes_dict)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_users_create():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    
    # Fetch all classes for assignment selection
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        password = request.form.get('password') or None
        nid = request.form.get('national_id') or None
        email = request.form.get('email') or None
        pw_hash = generate_password_hash(password) if password else None
        
        # Handle class assignments for teachers and staff
        assigned_classes = ''
        if role in ['teacher', 'staff']:
            selected_class_ids = request.form.getlist('assigned_classes')
            assigned_classes = ','.join(selected_class_ids) if selected_class_ids else ''
        
        conn.execute("INSERT INTO user (name, role, password_hash, national_id, email, classes) VALUES (?,?,?,?,?,?)",
                     (name, role, pw_hash, nid, email, assigned_classes))
        conn.commit()
        flash('User created', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', user=None, classes=classes)


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_users_edit(user_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    if not row:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    user = RowObject(row)
    
    # Fetch all classes for assignment selection
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        pw = request.form.get('password')
        nid = request.form.get('national_id') or None
        email = request.form.get('email') or None
        pw_hash = generate_password_hash(pw) if pw else row['password_hash']
        
        # Handle class assignments for teachers and staff
        assigned_classes = ''
        if role in ['teacher', 'staff']:
            selected_class_ids = request.form.getlist('assigned_classes')
            assigned_classes = ','.join(selected_class_ids) if selected_class_ids else ''
        
        conn.execute("UPDATE user SET name = ?, role = ?, password_hash = ?, national_id = ?, email = ?, classes = ? WHERE id = ?",
                     (name, role, pw_hash, nid, email, assigned_classes, user_id))
        conn.commit()
        flash('User updated', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin_user_form.html', user=user, classes=classes)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
    conn.commit()
    flash('User deleted', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
def admin_users_reset_password(user_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    if not row:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    user = RowObject(row)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password:
            flash('Password is required', 'danger')
        elif new_password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            pw_hash = generate_password_hash(new_password)
            conn.execute("UPDATE user SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
            conn.commit()
            flash(f'Password reset successfully for {user.name}', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin_reset_password.html', user=user)


@app.route('/admin/classes')
@login_required
def admin_classes():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in rows]
    return render_template('admin_classes.html', classes=classes)


@app.route('/admin/classes/create', methods=['GET', 'POST'])
@login_required
def admin_classes_create():
    if not admin_required():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        conn.execute("INSERT INTO school_class (name) VALUES (?)", (name,))
        conn.commit()
        flash('Class created', 'success')
        return redirect(url_for('admin_classes'))
    return render_template('admin_class_form.html', klass=None)


@app.route('/admin/classes/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_classes_edit(class_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM school_class WHERE id = ?", (class_id,)).fetchone()
    if not row:
        flash('Class not found', 'danger')
        return redirect(url_for('admin_classes'))
    klass = RowObject(row)
    if request.method == 'POST':
        name = request.form['name']
        conn.execute("UPDATE school_class SET name = ? WHERE id = ?", (name, class_id))
        conn.commit()
        flash('Class updated', 'success')
        return redirect(url_for('admin_classes'))
    return render_template('admin_class_form.html', klass=klass)


@app.route('/admin/classes/<int:class_id>/delete', methods=['POST'])
@login_required
def admin_classes_delete(class_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM school_class WHERE id = ?", (class_id,))
    conn.commit()
    flash('Class deleted', 'success')
    return redirect(url_for('admin_classes'))


@app.route('/admin/subjects')
@login_required
def admin_subjects():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    rows = conn.execute("SELECT * FROM subject ORDER BY name").fetchall()
    subjects = [RowObject(r) for r in rows]
    return render_template('admin_subjects.html', subjects=subjects)


@app.route('/admin/subjects/create', methods=['GET', 'POST'])
@login_required
def admin_subjects_create():
    if not admin_required():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        conn.execute("INSERT INTO subject (name) VALUES (?)", (name,))
        conn.commit()
        flash('Subject created', 'success')
        return redirect(url_for('admin_subjects'))
    return render_template('admin_subject_form.html', subject=None)


@app.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_subjects_edit(subject_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM subject WHERE id = ?", (subject_id,)).fetchone()
    if not row:
        flash('Subject not found', 'danger')
        return redirect(url_for('admin_subjects'))
    subject = RowObject(row)
    if request.method == 'POST':
        name = request.form['name']
        conn.execute("UPDATE subject SET name = ? WHERE id = ?", (name, subject_id))
        conn.commit()
        flash('Subject updated', 'success')
        return redirect(url_for('admin_subjects'))
    return render_template('admin_subject_form.html', subject=subject)


@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def admin_subjects_delete(subject_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM subject WHERE id = ?", (subject_id,))
    conn.commit()
    flash('Subject deleted', 'success')
    return redirect(url_for('admin_subjects'))


### Admin: Periods (schedule) ###
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@app.route('/admin/periods')
@login_required
def admin_periods():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    rows = conn.execute("SELECT * FROM period ORDER BY day_of_week, period").fetchall()
    periods = [RowObject(r) for r in rows]
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    subjects_rows = conn.execute("SELECT * FROM subject ORDER BY name").fetchall()
    subjects = [RowObject(r) for r in subjects_rows]
    return render_template('admin_periods.html', periods=periods, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/create', methods=['GET', 'POST'])
@login_required
def admin_periods_create():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    subjects_rows = conn.execute("SELECT * FROM subject ORDER BY name").fetchall()
    subjects = [RowObject(r) for r in subjects_rows]
    if request.method == 'POST':
        day = int(request.form.get('day_of_week'))
        period_no = int(request.form.get('period'))
        start_time = request.form.get('start_time') or None
        end_time = request.form.get('end_time') or None
        class_id = request.form.get('class_id') or None
        subject_id = request.form.get('subject_id') or None
        existing = conn.execute("SELECT id FROM period WHERE day_of_week = ? AND period = ? AND (class_id IS NULL OR class_id = ?)",
                                (day, period_no, class_id)).fetchone()
        if existing:
            flash('A period with the same day/number and class already exists', 'warning')
            return redirect(url_for('admin_periods'))
        conn.execute("INSERT INTO period (day_of_week, period, start_time, end_time, class_id, subject_id) VALUES (?,?,?,?,?,?)",
                     (day, period_no, start_time, end_time, class_id if class_id else None, subject_id if subject_id else None))
        conn.commit()
        flash('Period created', 'success')
        return redirect(url_for('admin_periods'))
    return render_template('admin_period_form.html', period=None, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_periods_edit(period_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM period WHERE id = ?", (period_id,)).fetchone()
    if not row:
        flash('Period not found', 'danger')
        return redirect(url_for('admin_periods'))
    p = RowObject(row)
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    subjects_rows = conn.execute("SELECT * FROM subject ORDER BY name").fetchall()
    subjects = [RowObject(r) for r in subjects_rows]
    if request.method == 'POST':
        new_day = int(request.form.get('day_of_week'))
        new_period = int(request.form.get('period'))
        new_start = request.form.get('start_time') or None
        new_end = request.form.get('end_time') or None
        new_class_id = request.form.get('class_id') or None
        new_subject_id = request.form.get('subject_id') or None
        existing = conn.execute("SELECT id FROM period WHERE day_of_week = ? AND period = ? AND (class_id IS NULL OR class_id = ?)",
                                (new_day, new_period, new_class_id)).fetchone()
        if existing and existing['id'] != period_id:
            flash('Another period with same day/number and class exists', 'warning')
            return redirect(url_for('admin_periods'))
        conn.execute("UPDATE period SET day_of_week = ?, period = ?, start_time = ?, end_time = ?, class_id = ?, subject_id = ? WHERE id = ?",
                     (new_day, new_period, new_start, new_end, new_class_id if new_class_id else None, new_subject_id if new_subject_id else None, period_id))
        conn.commit()
        flash('Period updated', 'success')
        return redirect(url_for('admin_periods'))
    return render_template('admin_period_form.html', period=p, classes=classes, subjects=subjects, days=DAYS)


@app.route('/admin/periods/<int:period_id>/delete', methods=['POST'])
@login_required
def admin_periods_delete(period_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM period WHERE id = ?", (period_id,))
    conn.commit()
    flash('Period deleted', 'success')
    return redirect(url_for('admin_periods'))


@app.cli.command('apply-unique-index')
def apply_unique_index():
    """Apply unique index for Period (safe for SQLite)."""
    # create unique index if not exists (SQLite supports IF NOT EXISTS)
    try:
        conn = get_db()
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_period_day_period_class_idx ON period (day_of_week, period, class_id);")
        conn.commit()
        print('Unique index applied (if it did not already exist).')
    except Exception as e:
        print('Failed to apply unique index:', e)


@app.cli.command('add-remark-column')
def add_remark_column():
    """Add remark column to attendance table (safe for existing databases)."""
    try:
        conn = get_db()
        # Check if remark column already exists
        cols = [c[1] for c in conn.execute("PRAGMA table_info(attendance)").fetchall()]
        if 'remark' not in cols:
            conn.execute("ALTER TABLE attendance ADD COLUMN remark TEXT")
            conn.commit()
            print('Added remark column to attendance table')
        else:
            print('Remark column already exists')
    except Exception as e:
        print('Failed to add remark column:', e)


@app.cli.command('add-attendance-columns')
def add_attendance_columns():
    """Add notes, created_at, and updated_at columns to attendance table (safe for existing databases)."""
    try:
        conn = get_db()
        cols = [c[1] for c in conn.execute("PRAGMA table_info(attendance)").fetchall()]
        
        if 'notes' not in cols:
            conn.execute("ALTER TABLE attendance ADD COLUMN notes TEXT")
            print('Added notes column to attendance table')
        else:
            print('Notes column already exists')
        
        if 'created_at' not in cols:
            conn.execute("ALTER TABLE attendance ADD COLUMN created_at TEXT")
            print('Added created_at column to attendance table')
        else:
            print('Created_at column already exists')
        
        if 'updated_at' not in cols:
            conn.execute("ALTER TABLE attendance ADD COLUMN updated_at TEXT")
            print('Added updated_at column to attendance table')
        else:
            print('Updated_at column already exists')
        
        conn.commit()
        print('Attendance columns update completed')
    except Exception as e:
        print('Failed to add attendance columns:', e)


@app.route('/admin/students')
@login_required
def admin_students():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    # fetch students with their class name (LEFT JOIN to include students without a class)
    rows = conn.execute(
        """
        SELECT s.*, c.name AS class_name
        FROM student s
        LEFT JOIN school_class c ON s.class_id = c.id
        ORDER BY s.class_id
        """
    ).fetchall()
    students = [RowObject(r) for r in rows]
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    return render_template('admin_students.html', students=students, classes=classes)


@app.route('/admin/students/create', methods=['GET', 'POST'])
@login_required
def admin_students_create():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    if request.method == 'POST':
        name = request.form['name']
        class_id = request.form.get('class_id') or None
        nid = request.form.get('national_id') or None
        conn.execute("INSERT INTO student (name, class_id, national_id) VALUES (?,?,?)", (name, class_id, nid))
        conn.commit()
        flash('Student created', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin_student_form.html', student=None, classes=classes)


@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_students_edit(student_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    row = conn.execute("SELECT * FROM student WHERE id = ?", (student_id,)).fetchone()
    if not row:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_students'))
    student = RowObject(row)
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    if request.method == 'POST':
        name = request.form['name']
        class_id = request.form.get('class_id') or None
        #nid = request.form.get('national_id') or None
        phone1 = request.form.get('phone1') or None
        conn.execute("UPDATE student SET name = ?, class_id = ?, phone1 = ? WHERE id = ?", (name, class_id, phone1, student_id))
        conn.commit()
        flash('Student updated', 'success')
        return redirect(url_for('admin_students'))
    return render_template('admin_student_form.html', student=student, classes=classes)


@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
def admin_students_delete(student_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM student WHERE id = ?", (student_id,))
    conn.commit()
    flash('Student deleted', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/attendance')
@login_required
def admin_attendance():
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    today = request.args.get('date') or get_current_date().isoformat()
    rows = conn.execute("""
        SELECT a.id, a.student_id, s.name as student_name, a.date, a.period, a.status, a.class_id, c.name as class_name, a.teacher_id, u.name as teacher_name
        FROM attendance a
        LEFT JOIN student s ON a.student_id = s.id
        LEFT JOIN school_class c ON a.class_id = c.id
        LEFT JOIN user u ON a.teacher_id = u.id
        WHERE a.date = ?
    """, (today,)).fetchall()
    records = [RowObject(r) for r in rows]
    return render_template('admin_attendance.html', records=records, today=today)


@app.route('/admin/attendance/<int:att_id>/delete', methods=['POST'])
@login_required
def admin_attendance_delete(att_id):
    if not admin_required():
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("DELETE FROM attendance WHERE id = ?", (att_id,))
    conn.commit()
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
        conn = get_db()
        # Expect sheets: students, teachers, classes, subjects
        if 'classes' in df:
            for _, row in df['classes'].iterrows():
                name = str(row.get('name') or row.get('class') or row.get('Class') or '').strip()
                if name:
                    exists = conn.execute("SELECT id FROM school_class WHERE name = ?", (name,)).fetchone()
                    if not exists:
                        conn.execute("INSERT INTO school_class (name) VALUES (?)", (name,))
        if 'students' in df:
            for _, row in df['students'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                class_name = str(row.get('class') or row.get('Class') or '').strip()
                nid = row.get('national_id') or row.get('national id') or row.get('nid') or row.get('NationalID') or row.get('NID')
                ph2 = str(row.get('phone2')).strip() if row.get('phone2') is not None else ''
                ph1 = str(row.get('phone1')).strip() if row.get('phone1') is not None else ''
                if name:
                    klass = conn.execute("SELECT id FROM school_class WHERE name = ?", (class_name,)).fetchone() if class_name else None
                    class_id = klass['id'] if klass else None
                    conn.execute("INSERT INTO student (name, class_id, national_id) VALUES (?,?,?)",
                                 (name, class_id, str(nid).strip() if nid is not None else None))
        if 'teachers' in df:
            for _, row in df['teachers'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                if name:
                    exists = conn.execute("SELECT id FROM user WHERE name = ? AND role = ?", (name, 'teacher')).fetchone()
                    if not exists:
                        nid = row.get('national_id') or row.get('national id') or row.get('nid')
                        conn.execute("INSERT INTO user (name, role, national_id) VALUES (?,?,?)", (name, 'teacher', str(nid).strip() if nid is not None else None))
        if 'subjects' in df:
            for _, row in df['subjects'].iterrows():
                name = str(row.get('name') or row.get('Name') or '').strip()
                if name:
                    exists = conn.execute("SELECT id FROM subject WHERE name = ?", (name,)).fetchone()
                    if not exists:
                        conn.execute("INSERT INTO subject (name) VALUES (?)", (name,))
        conn.commit()
        flash('Import completed', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('import.html')


@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    # fetch teachers/classes from sqlite so quick-login lists match imported/added rows
    conn = get_db()
    teachers_rows = conn.execute("SELECT * FROM user WHERE role = ? ORDER BY name", ('teacher',)).fetchall()
    teachers = [RowObject(r) for r in teachers_rows]
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    classes = [RowObject(r) for r in classes_rows]
    if request.method == 'POST':
        # Support email/password login for teachers
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            row = conn.execute("SELECT * FROM user WHERE email = ? AND role = ? LIMIT 1", (email.strip(), 'teacher')).fetchone()
            # fallback: allow using name as identifier if email column not populated
            if not row:
                row = conn.execute("SELECT * FROM user WHERE name = ? AND role = ? LIMIT 1", (email.strip(), 'teacher')).fetchone()
            if row:
                user = SimpleUser(row)
                if user.check_password(password):
                    login_user(user)
                    # show classes list after login
                    return redirect(url_for('teacher_classes'))
            flash('Invalid credentials', 'danger')
            return redirect(request.url)

        # existing quick-login (teacher + class selectors)
        teacher_id = request.form.get('teacher_id')
        class_id = request.form.get('class_id')
        if not teacher_id or not class_id:
            flash('Select teacher and class', 'warning')
            return redirect(request.url)
        session['teacher_id'] = int(teacher_id)
        session['class_id'] = int(class_id)
        return redirect(url_for('teacher_dashboard'))
    return render_template('teacher_login.html', teachers=teachers, classes=classes)


@app.route('/teacher/classes')
@login_required
def teacher_classes():
    # show list of classes assigned to current teacher
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db()
    tid = int(current_user.get_id())
    # try TeacherSubject mapping first
    rows = conn.execute("SELECT c.* FROM teacher_subject ts JOIN school_class c ON ts.class_id = c.id WHERE ts.teacher_id = ? ORDER BY c.name", (tid,)).fetchall()
    classes = [RowObject(r) for r in rows]
    # fallback to comma-separated `classes` field on user
    if not classes:
        urow = conn.execute("SELECT classes FROM user WHERE id = ?", (tid,)).fetchone()
        if urow and urow['classes']:
            for cid in str(urow['classes']).split(','):
                cid = cid.strip()
                if not cid:
                    continue
                crow = conn.execute("SELECT * FROM school_class WHERE id = ?", (cid,)).fetchone()
                if crow:
                    classes.append(RowObject(crow))
    return render_template('teacher_classes.html', classes=classes)


@app.route('/teacher/select_class/<int:class_id>')
@login_required
def teacher_select_class(class_id):
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    session['teacher_id'] = int(current_user.get_id())
    session['class_id'] = int(class_id)
    return redirect(url_for('teacher_dashboard'))


@app.route('/teacher/dashboard', methods=['GET', 'POST'])
def teacher_dashboard():
    teacher_id = session.get('teacher_id')
    class_id = session.get('class_id')
    if not teacher_id or not class_id:
        return redirect(url_for('teacher_login'))

    db_conn = get_db()
    # fetch teacher and class as RowObject wrappers (templates expect .id/.name access)
    trow = db_conn.execute("SELECT * FROM user WHERE id = ?", (teacher_id,)).fetchone()
    teacher = RowObject(trow) if trow else None
    crow = db_conn.execute("SELECT * FROM school_class WHERE id = ?", (class_id,)).fetchone()
    klass = RowObject(crow) if crow else None

    # students via sqlite
    students_rows = db_conn.execute("SELECT * FROM student WHERE class_id = ? ORDER BY name", (class_id,)).fetchall()
    students = [RowObject(r) for r in students_rows]

    today = get_current_date().isoformat()
    # compute today's periods for this class and current period based on time (sqlite)
    weekday = get_current_date().weekday()
    periods_rows = db_conn.execute(
        "SELECT * FROM period WHERE day_of_week = ? AND (class_id IS NULL OR class_id = ?) ORDER BY period",
        (weekday, class_id),
    ).fetchall()
    periods_today = [RowObject(r) for r in periods_rows]
    current_period = None
    now = get_current_datetime().time()
    def parse_t(tstr):
        try:
            return datetime.strptime(tstr, '%H:%M').time()
        except Exception:
            return None
    for p in periods_today:
        st = parse_t(p.start_time) if getattr(p, 'start_time', None) else None
        en = parse_t(p.end_time) if getattr(p, 'end_time', None) else None
        if st and en and st <= now <= en:
            current_period = p.period
            break

    if request.method == 'POST':
        # form contains period and statuses list
        period = int(request.form.get('period') or 1)
        current_time = get_current_datetime().isoformat()
        
        for student in students:
            status = request.form.get(f'status_{student.id}', 'present')
            existing = db_conn.execute("SELECT id, status FROM attendance WHERE student_id = ? AND date = ? AND period = ?", (student.id, today, period)).fetchone()
            if existing:
                # Clear remark if changing from absent to present
                if existing['status'] == 'absent' and status == 'present':
                    db_conn.execute("UPDATE attendance SET status = ?, class_id = ?, teacher_id = ?, remark = NULL, updated_at = ? WHERE id = ?",
                                    (status, class_id, teacher_id, current_time, existing['id']))
                else:
                    db_conn.execute("UPDATE attendance SET status = ?, class_id = ?, teacher_id = ?, updated_at = ? WHERE id = ?",
                                    (status, class_id, teacher_id, current_time, existing['id']))
            else:
                try:
                    db_conn.execute("INSERT INTO attendance (student_id, date, period, status, class_id, teacher_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                                    (student.id, today, period, status, class_id, teacher_id, current_time, current_time))
                except sqlite3.IntegrityError:
                    # fallback to update if unique constraint violated
                    db_conn.execute("UPDATE attendance SET status = ?, class_id = ?, teacher_id = ?, updated_at = ? WHERE student_id = ? AND date = ? AND period = ?",
                                    (status, class_id, teacher_id, current_time, student.id, today, period))
        db_conn.commit()
        # update daily Excel file
        update_daily_excel(today)
        flash('Attendance saved', 'success')
        return redirect(url_for('teacher_dashboard'))

    # build attendance map from sqlite
    attendance = {}
    rows = db_conn.execute("SELECT student_id, period, status FROM attendance WHERE date = ? AND class_id = ?", (today, class_id)).fetchall()
    for r in rows:
        attendance.setdefault(r['period'], {})[r['student_id']] = r['status']

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

    db_conn = get_db()
    classes_rows = db_conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    for krow in classes_rows:
        klass = RowObject(krow)
        
        # Try to find existing sheet by matching class name
        existing_sheet = None
        for sheet_name in wb.sheetnames:
            # Check if this sheet corresponds to the current class
            # Remove invalid characters from class name for comparison
            invalid_re = r"[:\\\\/?*\[\]]"
            clean_class_name = re.sub(invalid_re, '-', klass.name).strip()[:31]
            if sheet_name.startswith(clean_class_name):
                existing_sheet = sheet_name
                break
        
        if existing_sheet:
            ws = wb[existing_sheet]
        else:
            safe_name = get_safe_sheet_name(wb, klass.name)
            ws = wb.create_sheet(safe_name)
            ws.sheet_view.rightToLeft = True
        
        # Clear all existing content
        ws.delete_rows(1, ws.max_row)
        ws.append([f'التاريخ: {today_str}  الصف: {klass.name}'])
        
        # Get distinct periods that exist for this class today
        distinct_periods = db_conn.execute(
            "SELECT DISTINCT period FROM attendance WHERE date = ? AND class_id = ? ORDER BY period",
            (today_str, klass.id)
        ).fetchall()
        periods_list = [p['period'] for p in distinct_periods]
        
        # Build header row with actual periods
        students_rows = db_conn.execute("SELECT * FROM student WHERE class_id = ? ORDER BY name", (klass.id,)).fetchall()
        header = ['الطالب'] + [f'P{p}' for p in periods_list]
        ws.append(header)
        
        # Build student rows
        for srow in students_rows:
            s = RowObject(srow)
            row = [s.name]
            # fill from db with remark support for actual periods
            for period in periods_list:
                att = db_conn.execute("SELECT status, remark FROM attendance WHERE student_id = ? AND date = ? AND period = ? AND class_id = ?",
                                      (s.id, today_str, period, klass.id)).fetchone()
                if att:
                    if att['status'] == 'absent':
                        # Check if excused
                        if att['remark'] == 'excused':
                            row.append('E')  # Excused - counted as present
                        else:
                            row.append('A')  # Absent
                    else:
                        row.append('P')  # Present
                else:
                    row.append('')  # No record
            ws.append(row)

        # Add totals row per period (counts of P, E, and A)
        totals = ['الإجمالي']
        for period in periods_list:
            # Count truly absent (not excused)
            absent_row = db_conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ? AND (remark IS NULL OR remark != ?)",
                (today_str, klass.id, period, 'absent', 'excused'),
            ).fetchone()
            absent_cnt = absent_row['cnt'] if absent_row else 0
            
            # Count excused (marked absent but with excused remark)
            excused_row = db_conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ? AND remark = ?",
                (today_str, klass.id, period, 'absent', 'excused'),
            ).fetchone()
            excused_cnt = excused_row['cnt'] if excused_row else 0
            
            # Count present (including excused)
            present_row = db_conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ?",
                (today_str, klass.id, period, 'present'),
            ).fetchone()
            present_cnt = present_row['cnt'] if present_row else 0
            present_cnt += excused_cnt  # Add excused to present count
            
            totals.append(f"P:{present_cnt} A:{absent_cnt}")
        ws.append(totals)
        # style the totals row (bold + light fill + center)
        totals_row_idx = ws.max_row
        bold_font = Font(bold=True)
        fill = PatternFill(fill_type='solid', start_color='FFEFDB')  # light peach
        center_align = Alignment(horizontal='center')
        for col_idx in range(1, len(header) + 1):
            cell = ws.cell(row=totals_row_idx, column=col_idx)
            cell.font = bold_font
            cell.fill = fill
            cell.alignment = center_align

        # add teacher(s) who recorded attendance for this class/date under the totals row
        teacher_rows = db_conn.execute(
            "SELECT DISTINCT u.name FROM attendance a JOIN user u ON a.teacher_id = u.id WHERE a.date = ? AND a.class_id = ?",
            (today_str, klass.id),
        ).fetchall()
        teacher_names = ', '.join([tr['name'] for tr in teacher_rows]) if teacher_rows else ''
        teacher_row = ['المعلم:' , teacher_names] + ['' for _ in range(len(header)-2)] if len(header) > 1 else [f'المعلم: {teacher_names}']
        ws.append(teacher_row)
        # style teacher row (bold + lighter fill)
        teacher_row_idx = ws.max_row
        teacher_fill = PatternFill(fill_type='solid', start_color='FFF7E6')  # very light
        for col_idx in range(1, len(header) + 1):
            cell = ws.cell(row=teacher_row_idx, column=col_idx)
            cell.font = bold_font
            cell.fill = teacher_fill
            cell.alignment = center_align
    wb.save(fname)


@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    today = get_current_date().isoformat()
    conn = get_db()
    user_id = int(current_user.get_id())
    
    # Get staff user's assigned classes
    staff_row = conn.execute("SELECT classes FROM user WHERE id = ?", (user_id,)).fetchone()
    assigned_class_ids = []
    if staff_row and staff_row['classes']:
        assigned_class_ids = [cid.strip() for cid in str(staff_row['classes']).split(',') if cid.strip()]
    
    summary = []
    
    # If staff has assigned classes, show only those; otherwise show all
    if assigned_class_ids:
        placeholders = ','.join(['?' for _ in assigned_class_ids])
        classes_rows = conn.execute(f"SELECT * FROM school_class WHERE id IN ({placeholders}) ORDER BY name", assigned_class_ids).fetchall()
    else:
        classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    
    for krow in classes_rows:
        klass = RowObject(krow)
        
        # Get all students in the class
        students_rows = conn.execute("SELECT * FROM student WHERE class_id = ? ORDER BY name", (klass.id,)).fetchall()
        students_data = []
        
        present_count = 0
        absent_count = 0
        not_recorded_count = 0
        
        for srow in students_rows:
            student = RowObject(srow)
            # Get today's attendance for this student across all periods
            attendance_rows = conn.execute(
                "SELECT period, status, remark, notes FROM attendance WHERE student_id = ? AND date = ? AND class_id = ? ORDER BY period",
                (student.id, today, klass.id)
            ).fetchall()
            
            # Build period status dictionary with remarks and notes
            period_status = {}
            period_remarks = {}
            period_notes = {}
            student_has_any_record = False
            student_is_absent_today = False
            student_is_excused = False
            
            for att_row in attendance_rows:
                period_status[att_row['period']] = att_row['status']
                period_remarks[att_row['period']] = att_row['remark']
                period_notes[att_row['period']] = att_row['notes']
                student_has_any_record = True
                if att_row['status'] == 'absent':
                    # Check if excused - treat as present for counting
                    if att_row['remark'] == 'excused':
                        student_is_excused = True
                    else:
                        student_is_absent_today = True
            
            # Count overall status
            if not student_has_any_record:
                not_recorded_count += 1
                overall_status = 'not_recorded'
            elif student_is_absent_today:
                absent_count += 1
                overall_status = 'absent'
            else:
                present_count += 1
                overall_status = 'present' if student_has_any_record else 'not_recorded'
            
            students_data.append({
                'student': student,
                'period_status': period_status,
                'period_remarks': period_remarks,
                'period_notes': period_notes,
                'overall_status': overall_status
            })
        
        class_cp = get_current_period_for_class(klass.id)[0]
        
        # Calculate period-wise counts (present and absent for each period)
        # First, get the distinct periods that exist for this class today
        distinct_periods = conn.execute(
            "SELECT DISTINCT period FROM attendance WHERE date = ? AND class_id = ? ORDER BY period",
            (today, klass.id)
        ).fetchall()
        
        period_counts = {}
        for p_row in distinct_periods:
            p = p_row['period']
            
            present_cnt = conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ?",
                (today, klass.id, p, 'present')
            ).fetchone()['cnt']
            
            # Count truly absent (not excused)
            absent_cnt = conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ? AND (remark IS NULL OR remark != ?)",
                (today, klass.id, p, 'absent', 'excused')
            ).fetchone()['cnt']
            
            # Count excused
            excused_cnt = conn.execute(
                "SELECT COUNT(1) as cnt FROM attendance WHERE date = ? AND class_id = ? AND period = ? AND status = ? AND remark = ?",
                (today, klass.id, p, 'absent', 'excused')
            ).fetchone()['cnt']
            
            # Add excused to present count
            total_present = present_cnt + excused_cnt
            
            period_counts[p] = {
                'present': total_present,
                'absent': absent_cnt
            }
        
        summary.append({
            'class': klass,
            'total': len(students_rows),
            'present': present_count,
            'absent': absent_count,
            'not_recorded': not_recorded_count,
            'current_period': class_cp,
            'students': students_data,
            'period_counts': period_counts
        })
    
    # Global current period
    current_period, _ = get_current_period_for_class(None)
    
    return render_template('staff_dashboard.html', summary=summary, today=today, current_period=current_period, has_assigned_classes=bool(assigned_class_ids))


@app.route('/staff/update_remark', methods=['POST'])
@login_required
def staff_update_remark():
    if current_user.role != 'staff':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    student_id = request.form.get('student_id')
    date = request.form.get('date')
    period = request.form.get('period')
    remark = request.form.get('remark')
    
    # Validate inputs
    if not student_id or not date or not period:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    # Convert period to integer
    try:
        period = int(period)
    except (ValueError, TypeError):
        flash('Invalid period value', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    # Validate remark value - only 'excused' or 'still absent' allowed
    if remark not in ['excused', 'still absent', '']:
        flash('Invalid remark value', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    conn = get_db()
    current_time = get_current_datetime().isoformat()
    
    # Check if attendance record exists and student is absent
    att_record = conn.execute(
        "SELECT id, status FROM attendance WHERE student_id = ? AND date = ? AND period = ?",
        (int(student_id), date, period)
    ).fetchone()
    
    if not att_record:
        flash(f'Attendance record not found for period {period}', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    if att_record['status'] != 'absent':
        flash('Remarks can only be added for absent students', 'warning')
        return redirect(url_for('staff_dashboard'))
    
    # Update remark and updated_at timestamp
    conn.execute(
        "UPDATE attendance SET remark = ?, updated_at = ? WHERE id = ?",
        (remark if remark else None, current_time, att_record['id'])
    )
    conn.commit()
    
    # Regenerate Excel file with updated remark data
    update_daily_excel(date)
    
    # Provide user feedback based on remark type
    if remark == 'excused':
        flash('Student marked as excused (counted as present)', 'success')
    elif remark == 'still absent':
        flash('Student marked as still absent', 'info')
    else:
        flash('Remark cleared', 'success')
    
    # Force page reload by redirecting back
    return redirect(url_for('staff_dashboard'))


@app.route('/staff/update_notes', methods=['POST'])
@login_required
def staff_update_notes():
    if current_user.role != 'staff':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    student_id = request.form.get('student_id')
    date = request.form.get('date')
    period = request.form.get('period')
    notes = request.form.get('notes', '').strip()
    
    # Validate inputs
    if not student_id or not date or not period:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    # Convert period to integer
    try:
        period = int(period)
    except (ValueError, TypeError):
        flash('Invalid period value', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    conn = get_db()
    current_time = get_current_datetime().isoformat()
    
    # Check if attendance record exists
    att_record = conn.execute(
        "SELECT id FROM attendance WHERE student_id = ? AND date = ? AND period = ?",
        (int(student_id), date, period)
    ).fetchone()
    
    if not att_record:
        flash(f'Attendance record not found for period {period}', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    # Update notes and updated_at timestamp
    conn.execute(
        "UPDATE attendance SET notes = ?, updated_at = ? WHERE id = ?",
        (notes if notes else None, current_time, att_record['id'])
    )
    conn.commit()
    
    flash('Notes updated successfully', 'success')
    return redirect(url_for('staff_dashboard'))


@app.route('/staff/export_excel')
@login_required
def staff_export_excel():
    if current_user.role != 'staff':
        return redirect(url_for('index'))
    today = get_current_date().isoformat()
    # Regenerate the Excel file with latest data before sending
    update_daily_excel(today)
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
    today = get_current_date().isoformat()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    conn = get_db()
    classes_rows = conn.execute("SELECT * FROM school_class ORDER BY name").fetchall()
    for krow in classes_rows:
        klass = RowObject(krow)
        elements.append(Paragraph(f'Class: {klass.name} - Date: {today}', styles['Heading3']))
        students_rows = conn.execute("SELECT * FROM student WHERE class_id = ? ORDER BY name", (klass.id,)).fetchall()
        data = [['Student', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']]
        for srow in students_rows:
            s = RowObject(srow)
            row = [s.name]
            for p in range(1,7):
                att = conn.execute("SELECT status FROM attendance WHERE student_id = ? AND date = ? AND period = ? AND class_id = ?",
                                   (s.id, today, p, klass.id)).fetchone()
                row.append('A' if att and att['status']=='absent' else 'P' if att else '')
            data.append(row)
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, download_name=f'attendance-{today}.pdf', as_attachment=True)


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='10.108.97.179', port=5000)
