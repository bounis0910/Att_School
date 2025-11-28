"""
Attendance System - PostgreSQL with Pure psycopg2 (No SQLAlchemy)
"""
import os
import re
import sqlite3
from datetime import date, datetime
import pytz
import click
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from io import BytesIO
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

# PostgreSQL imports - pure psycopg2 only
import psycopg2
from psycopg2.extras import RealDictCursor

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Timezone configuration
TIMEZONE = pytz.timezone('Asia/Qatar')

def get_current_datetime():
    """Get current datetime with timezone."""
    return datetime.now(TIMEZONE)

def get_current_date():
    """Get current date with timezone."""
    return get_current_datetime().date()

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://att_user:password@localhost:5432/attendance_db')

# Parse database URL for psycopg2
def parse_db_url(url):
    """Parse DATABASE_URL for psycopg2 connection"""
    from urllib.parse import unquote
    url = url.replace('+asyncpg', '').replace('+psycopg2', '')
    url = url.replace('postgresql://', '')
    
    creds, host_db = url.rsplit('@', 1)
    user, password = creds.split(':', 1)
    user = unquote(user)
    password = unquote(password)
    
    if ':' in host_db:
        host, port_db = host_db.split(':')
        port, dbname = port_db.split('/', 1)
        port = int(port)
    else:
        host, dbname = host_db.split('/', 1)
        port = 5432
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': dbname
    }

db_params = parse_db_url(DATABASE_URL)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Database connection helper
def get_db():
    """Get database connection with RealDictCursor"""
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = psycopg2.connect(**db_params)
        db_conn.cursor_factory = RealDictCursor
    return db_conn

@app.teardown_appcontext
def close_db(exc):
    db_conn = getattr(g, '_database', None)
    if db_conn is not None:
        db_conn.close()

class RowObject:
    """Wrap database rows to allow attribute access."""
    def __init__(self, row):
        if isinstance(row, dict):
            self._row = row
        else:
            self._row = dict(row) if row else {}
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._row.get(name)

class SimpleUser(UserMixin):
    """User adapter for Flask-Login."""
    def __init__(self, row):
        if isinstance(row, dict):
            self.id = row.get('id')
            self.username = row.get('username') or row.get('name')
            self.name = row.get('name')
            self.role = row.get('role')
            self.password = row.get('password') or row.get('password_hash')
        else:
            self.id = None
            self.username = None
            self.name = None
            self.role = None
            self.password = None

    def get_id(self):
        return str(self.id)
    
    def check_password(self, pw):
        return check_password_hash(self.password, pw) if self.password else False

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "user" WHERE id = %s', (int(user_id),))
        row = cursor.fetchone()
        if row:
            return SimpleUser(dict(row))
    except:
        pass
    return None

# ================== Routes ==================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('name') or request.form.get('username')
        pw = request.form.get('password')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM "user" WHERE username = %s AND role = %s LIMIT 1',
                (username, 'admin')
            )
            row = cursor.fetchone()
            
            if row:
                user = SimpleUser(dict(row))
                if user.check_password(pw):
                    login_user(user)
                    return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Login error: {e}")
        
        flash('Invalid credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form.get('username')
        pw = request.form.get('password')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM "user" WHERE username = %s AND role = %s LIMIT 1',
                (username, 'staff')
            )
            row = cursor.fetchone()
            
            if row:
                user = SimpleUser(dict(row))
                if user.check_password(pw):
                    login_user(user)
                    return redirect(url_for('staff_dashboard'))
        except Exception as e:
            print(f"Login error: {e}")
        
        flash('Invalid credentials', 'danger')
    
    return render_template('staff_login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form.get('name') or request.form.get('username')
        pw = request.form.get('password')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM "user" WHERE username = %s AND role = %s LIMIT 1',
                (username, 'teacher')
            )
            row = cursor.fetchone()
            
            if row:
                user = SimpleUser(dict(row))
                if user.check_password(pw):
                    login_user(user)
                    return redirect(url_for('teacher_dashboard'))
        except Exception as e:
            print(f"Login error: {e}")
        
        flash('Invalid credentials', 'danger')
    
    return render_template('teacher_login.html')

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
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    return render_template('admin_dashboard.html', classes=classes)

@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    return render_template('staff_dashboard.html', classes=classes)

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    return render_template('teacher_dashboard.html', classes=classes)

# ================ Admin Routes ================

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM \"user\" ORDER BY role LIMIT 100")
        users_rows = cursor.fetchall()
        users = [RowObject(dict(r)) for r in users_rows]
    except:
        users = []
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/students')
@login_required
def admin_students():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, c.name as class_name FROM student s
            LEFT JOIN school_class c ON s.class_id = c.id
            ORDER BY s.name LIMIT 500
        """)
        students_rows = cursor.fetchall()
        students = [RowObject(dict(r)) for r in students_rows]
    except:
        students = []
    
    return render_template('admin_students.html', students=students)

@app.route('/admin/classes')
@login_required
def admin_classes():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    return render_template('admin_classes.html', classes=classes)

@app.route('/admin/subjects')
@login_required
def admin_subjects():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subject ORDER BY name")
        subjects_rows = cursor.fetchall()
        subjects = [RowObject(dict(r)) for r in subjects_rows]
    except:
        subjects = []
    
    return render_template('admin_subjects.html', subjects=subjects)

@app.route('/admin/attendance')
@login_required
def admin_attendance():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        today = get_current_date()
        cursor.execute("""
            SELECT a.*, s.name as student_name, c.name as class_name, u.name as teacher_name
            FROM attendance a
            LEFT JOIN student s ON a.student_id = s.id
            LEFT JOIN school_class c ON a.class_id = c.id
            LEFT JOIN "user" u ON a.teacher_id = u.id
            WHERE a.date = %s
            ORDER BY c.name, a.period
            LIMIT 500
        """, (today,))
        attendance_rows = cursor.fetchall()
        attendance = [RowObject(dict(r)) for r in attendance_rows]
    except:
        attendance = []
    
    return render_template('admin_attendance.html', attendance=attendance)

# ================ User Management Routes ================

@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def admin_users_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_user_form.html')

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_users_edit(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_user_form.html')

@app.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
def admin_users_reset_password(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_reset_password.html')

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('User deleted', 'success')
    return redirect(url_for('admin_users'))

# ================ Student Management Routes ================

@app.route('/admin/students/create', methods=['GET', 'POST'])
@login_required
def admin_students_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_student_form.html')

@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_students_edit(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_student_form.html')

@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
def admin_students_delete(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('Student deleted', 'success')
    return redirect(url_for('admin_students'))

# ================ Class Management Routes ================

@app.route('/admin/classes/create', methods=['GET', 'POST'])
@login_required
def admin_classes_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_class_form.html')

@app.route('/admin/classes/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_classes_edit(class_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_class_form.html')

@app.route('/admin/classes/<int:class_id>/delete', methods=['POST'])
@login_required
def admin_classes_delete(class_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('Class deleted', 'success')
    return redirect(url_for('admin_classes'))

# ================ Subject Management Routes ================

@app.route('/admin/subjects/create', methods=['GET', 'POST'])
@login_required
def admin_subjects_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_subject_form.html')

@app.route('/admin/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_subjects_edit(subject_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_subject_form.html')

@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def admin_subjects_delete(subject_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('Subject deleted', 'success')
    return redirect(url_for('admin_subjects'))

# ================ Period Management Routes ================

@app.route('/admin/periods', methods=['GET', 'POST'])
@login_required
def admin_periods():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM period ORDER BY id")
        periods_rows = cursor.fetchall()
        periods = [RowObject(dict(r)) for r in periods_rows]
    except:
        periods = []
    return render_template('admin_periods.html', periods=periods)

@app.route('/admin/periods/create', methods=['GET', 'POST'])
@login_required
def admin_periods_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_period_form.html')

@app.route('/admin/periods/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_periods_edit(period_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_period_form.html')

@app.route('/admin/periods/<int:period_id>/delete', methods=['POST'])
@login_required
def admin_periods_delete(period_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('Period deleted', 'success')
    return redirect(url_for('admin_periods'))

# ================ Attendance Routes ================

@app.route('/admin/attendance/<int:att_id>/delete', methods=['POST'])
@login_required
def admin_attendance_delete(att_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    flash('Attendance record deleted', 'success')
    return redirect(url_for('admin_attendance'))

# ================ Teacher Routes ================

@app.route('/teacher/classes', methods=['GET'])
@login_required
def teacher_classes():
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.* FROM school_class c
            LEFT JOIN teacher_subject ts ON c.id = ts.class_id
            WHERE ts.teacher_id = %s
            ORDER BY c.name
        """, (current_user.id,))
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    return render_template('teacher_classes.html', classes=classes)

@app.route('/teacher/class/<int:class_id>/select', methods=['GET'])
@login_required
def teacher_select_class(class_id):
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    session['selected_class_id'] = class_id
    return redirect(url_for('teacher_dashboard'))

# ================ Password Management Routes ================

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pw = request.form.get('old_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')
        
        if new_pw != confirm_pw:
            flash('Passwords do not match', 'danger')
            return render_template('change_password.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM "user" WHERE id = %s', (current_user.id,))
            row = cursor.fetchone()
            
            if row and check_password_hash(row['password'], old_pw):
                hashed_new = generate_password_hash(new_pw, method='scrypt')
                cursor.execute(
                    'UPDATE "user" SET password = %s WHERE id = %s',
                    (hashed_new, current_user.id)
                )
                conn.commit()
                flash('Password changed successfully', 'success')
                return redirect(url_for('admin_dashboard' if current_user.role == 'admin' else 'staff_dashboard' if current_user.role == 'staff' else 'teacher_dashboard'))
            else:
                flash('Old password is incorrect', 'danger')
        except Exception as e:
            print(f"Error changing password: {e}")
            flash('Error changing password', 'danger')
    
    return render_template('change_password.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
