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
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff_dashboard'))
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
        email = request.form.get('email')
        pw = request.form.get('password')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM "user" WHERE email = %s AND role = %s LIMIT 1',
                (email, 'staff')
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
        email = request.form.get('email')
        pw = request.form.get('password')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM "user" WHERE email = %s AND role = %s LIMIT 1',
                (email, 'teacher')
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
        
        # Get current user's assigned classes
        cursor.execute('SELECT classes FROM "user" WHERE id = %s', (current_user.id,))
        user_row = cursor.fetchone()
        
        classes = []
        if user_row and user_row['classes']:
            # Get class IDs assigned to this staff member
            class_ids_str = user_row['classes'].strip()
            if class_ids_str:
                class_ids = [cid.strip() for cid in class_ids_str.split(',') if cid.strip()]
                
                # Fetch only assigned classes
                if class_ids:
                    placeholders = ','.join(['%s'] * len(class_ids))
                    cursor.execute(
                        f"SELECT * FROM school_class WHERE id IN ({placeholders}) ORDER BY name",
                        class_ids
                    )
                    classes_rows = cursor.fetchall()
                    classes = [RowObject(dict(r)) for r in classes_rows]
    except Exception as e:
        print(f"Error loading staff dashboard: {e}")
        classes = []
    
    return render_template('staff_dashboard.html', classes=classes)

@app.route('/teacher/dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    # Get selected class from session
    class_id = session.get('selected_class_id')
    if not class_id:
        flash('Please select a class first', 'warning')
        return redirect(url_for('teacher_classes'))
    
    # Handle POST request (save attendance)
    if request.method == 'POST':
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            period = request.form.get('period')
            if not period:
                flash('Period not specified', 'danger')
                return redirect(url_for('teacher_dashboard'))
            
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Get all students for this class
            cursor.execute("SELECT id FROM student WHERE class_id = %s", (class_id,))
            student_rows = cursor.fetchall()
            
            # Save attendance for each student
            for student_row in student_rows:
                student_id = student_row['id']
                status_key = f'status_{student_id}'
                status = request.form.get(status_key, 'present')
                
                # Check if attendance record exists
                cursor.execute("""
                    SELECT id FROM attendance 
                    WHERE student_id = %s AND date = %s AND period = %s
                """, (student_id, today, period))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute("""
                        UPDATE attendance 
                        SET status = %s, teacher_id = %s, class_id = %s
                        WHERE id = %s
                    """, (status, current_user.id, class_id, existing['id']))
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO attendance (student_id, date, period, status, teacher_id, class_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (student_id, today, period, status, current_user.id, class_id))
            
            conn.commit()
            flash('Attendance saved successfully', 'success')
            return redirect(url_for('teacher_dashboard'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error saving attendance: {str(e)}', 'danger')
            return redirect(url_for('teacher_dashboard'))
    
    # GET request - display attendance form
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Fetch class info
        cursor.execute("SELECT * FROM school_class WHERE id = %s", (class_id,))
        klass_row = cursor.fetchone()
        if not klass_row:
            flash('Class not found', 'danger')
            return redirect(url_for('teacher_classes'))
        klass = RowObject(dict(klass_row))
        
        # Fetch teacher info
        cursor.execute('SELECT * FROM "user" WHERE id = %s', (current_user.id,))
        teacher_row = cursor.fetchone()
        teacher = RowObject(dict(teacher_row))
        
        # Get current date and day of week
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        day_of_week = datetime.now().weekday()  # Monday=0, Sunday=6
        day_of_week = (day_of_week + 1) % 7  # Convert to Sunday=0, Monday=1
        
        # Fetch periods for today
        cursor.execute("""
            SELECT * FROM period 
            WHERE day_of_week = %s 
            ORDER BY period_num
        """, (day_of_week,))
        periods_rows = cursor.fetchall()
        periods_today = [RowObject(dict(r)) for r in periods_rows]
        
        # Determine current period based on time
        current_time = datetime.now().time()
        current_period = None
        
        # First try to find period based on time range
        for p in periods_today:
            if p.start_time and p.end_time:
                if p.start_time <= current_time <= p.end_time:
                    current_period = p.period_num
                    break
        
        # If no period matches by time, use the first period of the day
        if current_period is None and periods_today:
            current_period = periods_today[0].period_num
        
        # Fetch students in this class
        cursor.execute("""
            SELECT * FROM student 
            WHERE class_id = %s 
            ORDER BY name
        """, (class_id,))
        students_rows = cursor.fetchall()
        students = [RowObject(dict(r)) for r in students_rows]
        
        # Fetch attendance records for today
        attendance = {}
        if current_period:
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE class_id = %s AND date = %s AND period = %s
            """, (class_id, today, current_period))
            attendance_rows = cursor.fetchall()
            attendance[current_period] = {}
            for row in attendance_rows:
                attendance[current_period][row['student_id']] = row['status']
        
        return render_template('teacher_dashboard.html', 
                             teacher=teacher,
                             klass=klass,
                             today=today,
                             current_period=current_period,
                             periods_today=periods_today,
                             students=students,
                             attendance=attendance)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('teacher_classes'))

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
        
        # Fetch classes for display
        cursor.execute("SELECT id, name FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes_dict = {str(c['id']): c['name'] for c in classes_rows}
    except:
        users = []
        classes_dict = {}
    
    return render_template('admin_users.html', users=users, classes_dict=classes_dict)

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
    
    if request.method == 'POST':
        username = request.form.get('name')
        role = request.form.get('role')
        password = request.form.get('password')
        national_id = request.form.get('national_id')
        email = request.form.get('email')
        assigned_classes = request.form.getlist('assigned_classes')
        
        if not username or not password or not role:
            flash('Username, password and role are required', 'danger')
            return render_template('admin_user_form.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT id FROM "user" WHERE username = %s', (username,))
            if cursor.fetchone():
                flash('Username already exists', 'danger')
                return render_template('admin_user_form.html')
            
            # Create new user
            hashed_pw = generate_password_hash(password, method='scrypt')
            
            # Prepare classes string
            classes_string = ','.join(assigned_classes) if assigned_classes else None
            
            cursor.execute(
                'INSERT INTO "user" (username, password, role, email, national_id, classes) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                (username, hashed_pw, role, email, national_id, classes_string)
            )
            new_user_id = cursor.fetchone()['id']
            
            conn.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            conn.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')
    
    # GET request - fetch classes for assignment
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    return render_template('admin_user_form.html', classes=classes)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_users_edit(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        username = request.form.get('name')
        role = request.form.get('role')
        password = request.form.get('password')
        national_id = request.form.get('national_id')
        email = request.form.get('email')
        assigned_classes = request.form.getlist('assigned_classes')
        
        try:
            # Prepare classes string
            classes_string = ','.join(assigned_classes) if assigned_classes else None
            
            # Update user
            if password:
                hashed_pw = generate_password_hash(password, method='scrypt')
                cursor.execute(
                    'UPDATE "user" SET username = %s, role = %s, password = %s, email = %s, national_id = %s, classes = %s WHERE id = %s',
                    (username, role, hashed_pw, email, national_id, classes_string, user_id)
                )
            else:
                cursor.execute(
                    'UPDATE "user" SET username = %s, role = %s, email = %s, national_id = %s, classes = %s WHERE id = %s',
                    (username, role, email, national_id, classes_string, user_id)
                )
            
            conn.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    # GET request - fetch user data
    cursor.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    
    user = RowObject(dict(user_row))
    
    # Fetch all classes and mark which ones are assigned to this user
    cursor.execute("SELECT * FROM school_class ORDER BY name")
    classes_rows = cursor.fetchall()
    classes = [RowObject(dict(r)) for r in classes_rows]
    
    # Strip the classes field since it's CHAR(100) with padding
    if user.classes:
        user.classes = user.classes.strip()
    else:
        user.classes = ''
    
    return render_template('admin_user_form.html', user=user, classes=classes)

@app.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
def admin_users_reset_password(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch user data
    cursor.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))
    
    user = RowObject(dict(user_row))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not new_password:
            flash('Password is required', 'danger')
        elif len(new_password) < 4:
            flash('Password must be at least 4 characters', 'danger')
        elif new_password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            # Hash and update password
            hashed_pw = generate_password_hash(new_password, method='scrypt')
            cursor.execute(
                'UPDATE "user" SET password = %s WHERE id = %s',
                (hashed_pw, user_id)
            )
            conn.commit()
            flash(f'Password reset successfully for user: {user.username}', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin_reset_password.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "user" WHERE id = %s', (user_id,))
        conn.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
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
        cursor.execute("SELECT * FROM period ORDER BY day_of_week, period_num")
        periods_rows = cursor.fetchall()
        periods = [RowObject(dict(r)) for r in periods_rows]
    except:
        periods = []
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return render_template('admin_periods.html', periods=periods, days=days)

@app.route('/admin/periods/create', methods=['GET', 'POST'])
@login_required
def admin_periods_create():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        period_num = request.form.get('period')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        class_id = request.form.get('class_id')
        subject_id = request.form.get('subject_id')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if period already exists for this day
            cursor.execute(
                'SELECT id FROM period WHERE day_of_week = %s AND period_num = %s',
                (day_of_week, period_num)
            )
            existing = cursor.fetchone()
            
            if existing:
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                flash(f'Period {period_num} already exists for {days[int(day_of_week)]}. Please choose a different period number or day.', 'danger')
                # Re-fetch data for form
                cursor.execute("SELECT * FROM school_class ORDER BY name")
                classes_rows = cursor.fetchall()
                classes = [RowObject(dict(r)) for r in classes_rows]
                
                cursor.execute("SELECT * FROM subject ORDER BY name")
                subjects_rows = cursor.fetchall()
                subjects = [RowObject(dict(r)) for r in subjects_rows]
                
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                return render_template('admin_period_form.html', classes=classes, subjects=subjects, days=days)
            
            cursor.execute(
                '''INSERT INTO period (day_of_week, period_num, start_time, end_time, class_id, teacher_id, created_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, NOW()) RETURNING id''',
                (day_of_week, period_num, start_time if start_time else None, 
                 end_time if end_time else None, class_id if class_id else None, None)
            )
            
            conn.commit()
            flash('Period created successfully', 'success')
            return redirect(url_for('admin_periods'))
        except Exception as e:
            conn.rollback()
            if 'unique_day_period' in str(e).lower() or 'duplicate' in str(e).lower():
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                flash(f'Period {period_num} already exists for {days[int(day_of_week)]}. Please choose a different period number or day.', 'danger')
            else:
                flash(f'Error creating period: {str(e)}', 'danger')
    
    # GET request
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
        
        cursor.execute("SELECT * FROM subject ORDER BY name")
        subjects_rows = cursor.fetchall()
        subjects = [RowObject(dict(r)) for r in subjects_rows]
    except:
        classes = []
        subjects = []
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return render_template('admin_period_form.html', classes=classes, subjects=subjects, days=days)

@app.route('/admin/periods/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_periods_edit(period_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        period_num = request.form.get('period')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        class_id = request.form.get('class_id')
        subject_id = request.form.get('subject_id')
        
        try:
            # Check if another period exists with same day and period_num (excluding current one)
            cursor.execute(
                'SELECT id FROM period WHERE day_of_week = %s AND period_num = %s AND id != %s',
                (day_of_week, period_num, period_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                flash(f'Period {period_num} already exists for {days[int(day_of_week)]}. Please choose a different period number or day.', 'danger')
                # Re-fetch data for form
                cursor.execute('SELECT * FROM period WHERE id = %s', (period_id,))
                period_row = cursor.fetchone()
                period = RowObject(dict(period_row))
                
                cursor.execute("SELECT * FROM school_class ORDER BY name")
                classes_rows = cursor.fetchall()
                classes = [RowObject(dict(r)) for r in classes_rows]
                
                cursor.execute("SELECT * FROM subject ORDER BY name")
                subjects_rows = cursor.fetchall()
                subjects = [RowObject(dict(r)) for r in subjects_rows]
                
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                return render_template('admin_period_form.html', period=period, classes=classes, subjects=subjects, days=days)
            
            cursor.execute(
                '''UPDATE period SET day_of_week = %s, period_num = %s, start_time = %s, 
                   end_time = %s, class_id = %s WHERE id = %s''',
                (day_of_week, period_num, start_time if start_time else None,
                 end_time if end_time else None, class_id if class_id else None, period_id)
            )
            
            conn.commit()
            flash('Period updated successfully', 'success')
            return redirect(url_for('admin_periods'))
        except Exception as e:
            conn.rollback()
            if 'unique_day_period' in str(e).lower() or 'duplicate' in str(e).lower():
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                flash(f'Period {period_num} already exists for {days[int(day_of_week)]}. Please choose a different period number or day.', 'danger')
            else:
                flash(f'Error updating period: {str(e)}', 'danger')
    
    # GET request - fetch period data
    cursor.execute('SELECT * FROM period WHERE id = %s', (period_id,))
    period_row = cursor.fetchone()
    
    if not period_row:
        flash('Period not found', 'danger')
        return redirect(url_for('admin_periods'))
    
    period = RowObject(dict(period_row))
    
    # Fetch classes and subjects
    cursor.execute("SELECT * FROM school_class ORDER BY name")
    classes_rows = cursor.fetchall()
    classes = [RowObject(dict(r)) for r in classes_rows]
    
    cursor.execute("SELECT * FROM subject ORDER BY name")
    subjects_rows = cursor.fetchall()
    subjects = [RowObject(dict(r)) for r in subjects_rows]
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return render_template('admin_period_form.html', period=period, classes=classes, subjects=subjects, days=days)

@app.route('/admin/periods/<int:period_id>/delete', methods=['POST'])
@login_required
def admin_periods_delete(period_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM period WHERE id = %s', (period_id,))
        conn.commit()
        flash('Period deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting period: {str(e)}', 'danger')
    
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
        
        # Get teacher's assigned classes from user.classes column
        cursor.execute('SELECT classes FROM "user" WHERE id = %s', (current_user.id,))
        user_row = cursor.fetchone()
        
        classes = []
        if user_row and user_row['classes']:
            class_ids_str = user_row['classes'].strip()
            if class_ids_str:
                class_ids = [cid.strip() for cid in class_ids_str.split(',') if cid.strip()]
                if class_ids:
                    placeholders = ','.join(['%s'] * len(class_ids))
                    cursor.execute(
                        f"SELECT * FROM school_class WHERE id IN ({placeholders}) ORDER BY name",
                        class_ids
                    )
                    classes_rows = cursor.fetchall()
                    classes = [RowObject(dict(r)) for r in classes_rows]
        
        # Get current day of week and periods for today
        from datetime import datetime
        day_of_week = datetime.now().weekday()  # Monday=0, Sunday=6
        day_of_week = (day_of_week + 1) % 7  # Convert to Sunday=0, Monday=1
        
        cursor.execute("""
            SELECT * FROM period 
            WHERE day_of_week = %s 
            ORDER BY period_num
        """, (day_of_week,))
        periods_rows = cursor.fetchall()
        periods_today = [RowObject(dict(r)) for r in periods_rows]
        
        # Determine current period based on time
        current_time = datetime.now().time()
        current_period = None
        
        for p in periods_today:
            if p.start_time and p.end_time:
                if p.start_time <= current_time <= p.end_time:
                    current_period = p.period_num
                    break
        
        # Day names in Arabic
        days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        today_name = days[day_of_week]
        
    except Exception as e:
        print(f"Error loading teacher classes: {e}")
        classes = []
        periods_today = []
        current_period = None
        today_name = ''
    
    return render_template('teacher_classes.html', 
                         classes=classes, 
                         periods_today=periods_today,
                         current_period=current_period,
                         today_name=today_name)

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
