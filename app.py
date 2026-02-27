"""
Attendance System - PostgreSQL with Pure psycopg2 (No SQLAlchemy)
"""
import os

from datetime import date, datetime
import pytz
import secrets
import json
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
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:Almana@Pg23@localhost:5432/alsisdb')

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


# --- CSRF helpers ---
def _generate_csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(16)
        session['_csrf_token'] = token
    return token

def validate_csrf(token):
    stored = session.get('_csrf_token')
    return bool(stored and token and secrets.compare_digest(stored, token))


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=_generate_csrf_token)


@app.context_processor
def inject_now():
    # Provide a `now()` callable to templates that returns current date string
    return dict(now=lambda: get_current_date().strftime('%Y-%m-%d'))

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
        # Prepare container for violation types
        violation_types = []
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
            import traceback
            tb = traceback.format_exc()
            print(f"Login error: {e}\n{tb}")
            try:
                with open('/tmp/teacher_login_error.log','a') as fh:
                    fh.write('\n--- teacher_login exception ---\n')
                    fh.write(tb)
            except Exception:
                pass
        
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


@app.route('/admin/violations_week')
@login_required
def admin_violations_week():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        from datetime import date
        conn = get_db(); cursor = conn.cursor()
        # determine week/year params
        week = request.args.get('week')
        year = request.args.get('year')
        class_id = request.args.get('class_id')
        today = date.today()
        try:
            if week:
                week = int(week)
            else:
                week = today.isocalendar()[1]
            if year:
                year = int(year)
            else:
                year = today.isocalendar()[0]
        except Exception:
            week = today.isocalendar()[1]
            year = today.isocalendar()[0]

        # compute monday/sunday of ISO week
        try:
            from datetime import date as Date
            monday = Date.fromisocalendar(year, week, 1)
            sunday = Date.fromisocalendar(year, week, 7)
        except Exception:
            monday = today
            sunday = today

        params = [monday.isoformat(), sunday.isoformat()]
        where_cls = ''
        if class_id:
            where_cls = ' AND v.class_id = %s'
            params.append(int(class_id))

        # aggregate by violation name and class
        sql = f"SELECT v.violation_name, c.name as class_name, COUNT(*) as cnt FROM violation v LEFT JOIN school_class c ON v.class_id = c.id WHERE v.date >= %s AND v.date <= %s {where_cls} GROUP BY v.violation_name, c.name ORDER BY cnt DESC"
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()

        # Also fetch classes for filter
        cursor.execute('SELECT id, name FROM school_class ORDER BY name')
        classes_rows = cursor.fetchall()

        return render_template('admin_violations_week.html', rows=rows, monday=monday, sunday=sunday, week=week, year=year, classes=classes_rows, sel_class=class_id)
    except Exception as e:
        tb = traceback.format_exc(); print(tb)
        flash(f'Error loading weekly violations: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/violations_week/export')
@login_required
def admin_violations_week_export():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        from datetime import date
        conn = get_db(); cursor = conn.cursor()
        week = request.args.get('week')
        year = request.args.get('year')
        class_id = request.args.get('class_id')
        today = date.today()
        try:
            if week:
                week = int(week)
            else:
                week = today.isocalendar()[1]
            if year:
                year = int(year)
            else:
                year = today.isocalendar()[0]
        except Exception:
            week = today.isocalendar()[1]
            year = today.isocalendar()[0]
        try:
            from datetime import date as Date
            monday = Date.fromisocalendar(year, week, 1)
            sunday = Date.fromisocalendar(year, week, 7)
        except Exception:
            monday = today
            sunday = today

        params = [monday.isoformat(), sunday.isoformat()]
        where_cls = ''
        if class_id:
            where_cls = ' AND v.class_id = %s'
            params.append(int(class_id))

        sql = f"SELECT v.violation_name, c.name as class_name, COUNT(*) as cnt FROM violation v LEFT JOIN school_class c ON v.class_id = c.id WHERE v.date >= %s AND v.date <= %s {where_cls} GROUP BY v.violation_name, c.name ORDER BY cnt DESC"
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()

        # build Excel
        wb = Workbook()
        ws = wb.active
        ws.title = f'Violations W{week}-{year}'
        ws.append(['Violation', 'Class', 'Count'])
        for r in rows:
            ws.append([r.get('violation_name'), r.get('class_name'), r.get('cnt')])

        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        fname = f'violations_week_{week}_{year}.xlsx'
        return send_file(bio, as_attachment=True, download_name=fname, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        tb = traceback.format_exc(); print(tb)
        flash(f'Error exporting weekly violations: {e}', 'danger')
        return redirect(url_for('admin_violations_week'))

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
        if user_row and user_row.get('classes'):
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
        
        # Build summary structure expected by the template
        summary = []
        has_assigned_classes = len(classes) > 0

        # Get current date and periods for today
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        day_of_week = datetime.now().weekday()
        day_of_week = (day_of_week + 1) % 7

        cursor.execute("SELECT * FROM period WHERE day_of_week = %s ORDER BY period_num", (day_of_week,))
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
        if current_period is None and periods_today:
            current_period = periods_today[0].period_num

        # For each assigned class, compute counts and per-student details
        for cls in classes:
            # fetch students
            cursor.execute("SELECT * FROM student WHERE class_id = %s ORDER BY name", (cls.id,))
            students_rows = cursor.fetchall()
            students = [RowObject(dict(r)) for r in students_rows]

            # fetch attendance for this class and today
            cursor.execute("SELECT * FROM attendance WHERE class_id = %s AND date = %s", (cls.id, today))
            attendance_rows = cursor.fetchall()

            # build period_counts
            period_counts = {}
            period_nums = [p.period_num for p in periods_today]
            for pn in period_nums:
                period_counts[pn] = {'present': 0, 'absent': 0}
            for ar in attendance_rows:
                pn = ar['period']
                if pn not in period_counts:
                    period_counts[pn] = {'present': 0, 'absent': 0}
                if ar['status'] == 'present':
                    period_counts[pn]['present'] += 1
                else:
                    period_counts[pn]['absent'] += 1

            # build per-student breakdown
            student_items = []
            present_count = 0
            absent_count = 0
            not_recorded_count = 0

            # index attendance by student and period
            att_index = {}
            for ar in attendance_rows:
                sid = ar['student_id']
                pn = ar['period']
                if sid not in att_index:
                    att_index[sid] = {}
                att_index[sid][pn] = ar

            for s in students:
                item = {
                    'student': s,
                    'period_status': {},
                    'period_remarks': {},
                    'period_notes': {},
                }
                any_present = False
                any_absent = False
                for pn in period_nums:
                    rec = att_index.get(s.id, {}).get(pn)
                    if rec:
                        status = rec['status']
                        item['period_status'][pn] = status
                        item['period_remarks'][pn] = rec.get('remark')
                        item['period_notes'][pn] = rec.get('notes')
                        if status == 'present':
                            any_present = True
                        elif status == 'absent':
                            any_absent = True
                    else:
                        item['period_status'][pn] = None
                        item['period_remarks'][pn] = None
                        item['period_notes'][pn] = None

                if any_present:
                    item['overall_status'] = 'present'
                    present_count += 1
                elif any_absent:
                    item['overall_status'] = 'absent'
                    absent_count += 1
                else:
                    item['overall_status'] = 'not_recorded'
                    not_recorded_count += 1

                student_items.append(item)

            summary.append({
                'class': cls,
                'current_period': current_period,
                'total': len(students),
                'present': present_count,
                'absent': absent_count,
                'not_recorded': not_recorded_count,
                'period_counts': period_counts,
                'students': student_items,
            })
    except Exception as e:
        print(f"Error loading staff dashboard: {e}")
        classes = []
        summary = []
        has_assigned_classes = False

    return render_template('staff_dashboard.html', classes=classes, summary=summary, has_assigned_classes=has_assigned_classes, today=today)


@app.route('/staff/violations')
@login_required
def staff_violations():
    if current_user.role not in ['admin', 'staff']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Get classes assigned to this staff user
        cursor.execute('SELECT classes FROM "user" WHERE id = %s', (current_user.id,))
        user_row = cursor.fetchone()
        classes = []
        if user_row and user_row.get('classes'):
            class_ids_str = user_row['classes'].strip()
            if class_ids_str:
                class_ids = [cid.strip() for cid in class_ids_str.split(',') if cid.strip()]
                if class_ids:
                    placeholders = ','.join(['%s'] * len(class_ids))
                    cursor.execute(f"SELECT * FROM school_class WHERE id IN ({placeholders}) ORDER BY name", class_ids)
                    classes_rows = cursor.fetchall()
                    classes = [RowObject(dict(r)) for r in classes_rows]

        # Ensure violation table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violation (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                class_id INTEGER,
                staff_id INTEGER,
                violation_name TEXT,
                lesson_name TEXT,
                period INTEGER,
                statement_of_receipt TEXT,
                parental_consent VARCHAR(32),
                referral TEXT,
                date DATE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        # Ensure audit table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violation_audit (
                id SERIAL PRIMARY KEY,
                violation_id INTEGER,
                action VARCHAR(32),
                user_id INTEGER,
                username TEXT,
                details JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # Ensure a separate table exists to manage the list of violation names (types)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violation_type (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                status VARCHAR(32) NOT NULL DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # Fetch active violation types for the staff assignment form
        try:
            cursor.execute("SELECT id, name FROM violation_type WHERE status = %s ORDER BY name", ('active',))
            vt_rows = cursor.fetchall()
            violation_types = [RowObject(dict(r)) for r in vt_rows]
        except Exception:
            violation_types = []

        # Fetch subjects for lesson selection
        try:
            cursor.execute("SELECT id, name FROM subject ORDER BY name")
            subj_rows = cursor.fetchall()
            subjects = [RowObject(dict(r)) for r in subj_rows]
        except Exception:
            subjects = []

        # Build data: for each class fetch students and their violations
        classes_data = []
        for cls in classes:
            cursor.execute("SELECT * FROM student WHERE class_id = %s ORDER BY name", (cls.id,))
            students_rows = cursor.fetchall()
            students = [RowObject(dict(r)) for r in students_rows]

            # fetch periods for this class
            cursor.execute("SELECT * FROM period WHERE class_id = %s ORDER BY period_num", (cls.id,))
            periods_rows_cls = cursor.fetchall()
            periods_for_class = [RowObject(dict(r)) for r in periods_rows_cls]

            # If no class-specific periods are defined, fall back to day-of-week periods (global)
            if not periods_for_class:
                try:
                    from datetime import datetime
                    day_of_week = datetime.now().weekday()
                    day_of_week = (day_of_week + 1) % 7
                    cursor.execute("SELECT * FROM period WHERE day_of_week = %s ORDER BY period_num", (day_of_week,))
                    fallback_rows = cursor.fetchall()
                    periods_for_class = [RowObject(dict(r)) for r in fallback_rows]
                except Exception:
                    periods_for_class = []

            # fetch violations for students in this class (include staff info)
            student_ids = [s.id for s in students]
            violations_by_student = {}
            if student_ids:
                placeholders = ','.join(['%s'] * len(student_ids))
                cursor.execute(
                    f"SELECT v.*, u.username as staff_username, u.username as staff_name "
                    f"FROM violation v LEFT JOIN \"user\" u ON v.staff_id = u.id "
                    f"WHERE v.student_id IN ({placeholders}) ORDER BY v.created_at DESC",
                    student_ids
                )
                viol_rows = cursor.fetchall()
                for vr in viol_rows:
                    sid = vr['student_id']
                    if sid not in violations_by_student:
                        violations_by_student[sid] = []
                    violations_by_student[sid].append(RowObject(dict(vr)))

            students_with_viol = []
            for s in students:
                students_with_viol.append({
                    'student': s,
                    'violations': violations_by_student.get(s.id, [])
                })

            classes_data.append({'class': cls, 'students': students_with_viol, 'periods': periods_for_class})

        # --- Paginated / filterable overall violations list ---
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        filter_class = request.args.get('class_id', type=int)
        filter_student = request.args.get('student_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        where_clauses = []
        params = []
        if filter_class:
            where_clauses.append('v.class_id = %s')
            params.append(filter_class)
        if filter_student:
            where_clauses.append('v.student_id = %s')
            params.append(filter_student)
        if start_date:
            where_clauses.append('v.date >= %s')
            params.append(start_date)
        if end_date:
            where_clauses.append('v.date <= %s')
            params.append(end_date)

        where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''

        # total count
        count_sql = f"SELECT COUNT(*) as cnt FROM violation v {where_sql}"
        cursor.execute(count_sql, tuple(params))
        cnt_row = cursor.fetchone()
        total = cnt_row['cnt'] if cnt_row else 0

        offset = (page - 1) * per_page
        select_sql = (
            f"SELECT v.*, s.name as student_name, c.name as class_name, u.username as staff_username, u.username as staff_name "
            f"FROM violation v LEFT JOIN student s ON v.student_id = s.id LEFT JOIN school_class c ON v.class_id = c.id LEFT JOIN \"user\" u ON v.staff_id = u.id {where_sql} "
            f"ORDER BY v.created_at DESC LIMIT %s OFFSET %s"
        )
        exec_params = tuple(params) + (per_page, offset)
        cursor.execute(select_sql, exec_params)
        paged_rows = cursor.fetchall()
        paged_violations = [RowObject(dict(r)) for r in paged_rows]

        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if per_page else 1
        }

        return render_template('staff_violations.html', classes_data=classes_data, paged_violations=paged_violations, pagination=pagination, filter_class=filter_class, filter_student=filter_student, start_date=start_date, end_date=end_date, violation_types=violation_types, subjects=subjects)

    except Exception as e:
        import traceback, os
        tb = traceback.format_exc()
        print(f"Error loading staff violations: {e}\n{tb}")
        # write trace to temp file for inspection
        try:
            p = '/tmp/violations_trace.log'
            with open(p, 'a') as fh:
                fh.write('\n---\n')
                fh.write(tb)
        except Exception:
            pass

        # If admin, show the traceback inline to help debugging
        if current_user.is_authenticated and getattr(current_user, 'role', None) == 'admin':
            return render_template('admin_violations_error.html', error=tb), 500

        flash('Error loading violations', 'danger')
        return redirect(url_for('staff_dashboard'))


@app.route('/api/students')
@login_required
def api_students():
    q = request.args.get('q', '').strip()
    if not q:
        return {'results': []}, 200
    try:
        conn = get_db()
        cursor = conn.cursor()
        like = f"%{q}%"
        cursor.execute("SELECT id, name FROM student WHERE name ILIKE %s ORDER BY name LIMIT 20", (like,))
        rows = cursor.fetchall()
        results = [{'id': r['id'], 'name': r['name']} for r in rows]
        return results
    except Exception as e:
        return [], 200


@app.route('/staff/assign_violation', methods=['POST'])
@login_required
def staff_assign_violation():
    if current_user.role not in ['admin', 'staff']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    try:
        student_id = request.form.get('student_id')
        class_id = request.form.get('class_id')

        # require class selection
        if not class_id:
            flash('Please select a class before assigning performance','danger')
            return redirect(request.referrer or url_for('teacher_assign_performance'))
        date_val = request.form.get('date')
        violation_name = request.form.get('violation_name')
        lesson_name = request.form.get('lesson_name')
        period = request.form.get('period')
        statement_of_receipt = request.form.get('statement_of_receipt')
        parental_consent = request.form.get('parental_consent')
        referral = request.form.get('referral')

        # CSRF
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(request.referrer or url_for('staff_violations'))

        # Basic validation
        if not student_id or not violation_name:
            flash('Student and violation name are required', 'danger')
            return redirect(request.referrer or url_for('staff_violations'))
        if parental_consent and parental_consent not in ('consent', 'refusal'):
            flash('Invalid parental consent value', 'danger')
            return redirect(request.referrer or url_for('staff_violations'))

        conn = get_db()
        cursor = conn.cursor()

        # Ensure table exists (simple migration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violation (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                class_id INTEGER,
                staff_id INTEGER,
                violation_name TEXT,
                lesson_name TEXT,
                period INTEGER,
                statement_of_receipt TEXT,
                parental_consent VARCHAR(32),
                referral TEXT,
                date DATE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        cursor.execute("""
            INSERT INTO violation (student_id, class_id, staff_id, violation_name, lesson_name, period, statement_of_receipt, parental_consent, referral, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            int(student_id), int(class_id) if class_id else None, int(current_user.id), violation_name, lesson_name, int(period) if period else None,
            statement_of_receipt, parental_consent, referral, date_val
        ))

        inserted = cursor.fetchone()
        viol_id = inserted['id'] if inserted and 'id' in inserted else None
        # Insert audit record
        try:
            details = json.dumps({'violation_name': violation_name, 'lesson_name': lesson_name, 'period': period})
            cursor.execute('INSERT INTO violation_audit (violation_id, action, user_id, username, details) VALUES (%s,%s,%s,%s,%s)', (viol_id, 'create', current_user.id, getattr(current_user, 'username', None), details))
        except Exception:
            pass

        conn.commit()
        flash('Violation assigned successfully', 'success')
        return redirect(request.referrer or url_for('staff_violations'))
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        flash(f'Error assigning violation: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('staff_violations'))

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


@app.route('/teacher/assign_violation', methods=['GET','POST'])
@login_required
def teacher_assign_violation():
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        conn = get_db(); cursor = conn.cursor()
        # Fetch classes assigned to this teacher
        cursor.execute('SELECT classes FROM "user" WHERE id = %s', (current_user.id,))
        user_row = cursor.fetchone()
        classes = []
        if user_row and user_row.get('classes'):
            class_ids_str = user_row['classes'].strip()
            if class_ids_str:
                class_ids = [cid.strip() for cid in class_ids_str.split(',') if cid.strip()]
                if class_ids:
                    placeholders = ','.join(['%s'] * len(class_ids))
                    cursor.execute(f"SELECT id, name FROM school_class WHERE id IN ({placeholders}) ORDER BY name", class_ids)
                    classes = cursor.fetchall()

        # Ensure violation_type table exists and load active types

        try:
            cursor.execute("SELECT id, name FROM violation_type WHERE status = %s ORDER BY name", ('active',))
            violation_types = cursor.fetchall()
        except Exception:
            violation_types = []

        sel_class = request.args.get('class_id')
        students = []
        viol_by_student = {}
        viol_list_by_student = {}
        from datetime import date, timedelta
        today = date.today()
        default_date = today.isoformat()

        if sel_class:
            cursor.execute('SELECT id, name, roll_number FROM student WHERE class_id = %s ORDER BY roll_number NULLS LAST, name', (int(sel_class),))
            students = cursor.fetchall()

            # Ensure violation table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS violation (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL,
                    class_id INTEGER,
                    staff_id INTEGER,
                    violation_name TEXT,
                    lesson_name TEXT,
                    period INTEGER,
                    statement_of_receipt TEXT,
                    parental_consent VARCHAR(32),
                    referral TEXT,
                    date DATE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')

            # build student id list
            student_ids = [str(s['id']) for s in students]
            if student_ids:
                placeholders = ','.join(['%s'] * len(student_ids))
                sid_params = [int(x) for x in student_ids]

                # compute current week range (Monday..Sunday)
                try:
                    wd = today.isoweekday()
                    monday = today - timedelta(days=(wd-1))
                    sunday = monday + timedelta(days=6)
                except Exception:
                    monday = today
                    sunday = today

                # load violations by this teacher for the week to prefill per-student selection
                try:
                    params = [int(sel_class), monday.isoformat(), sunday.isoformat(), int(current_user.id)] + sid_params
                    cursor.execute(f"SELECT * FROM violation WHERE class_id = %s AND date >= %s AND date <= %s AND staff_id = %s AND student_id IN ({placeholders})", tuple(params))
                    prow = cursor.fetchall()
                    for pr in prow:
                        viol_by_student[pr['student_id']] = dict(pr)
                except Exception:
                    viol_by_student = {}

                # load ALL violations for those students for the same week (include staff name)
                try:
                    params_all = [int(sel_class), monday.isoformat(), sunday.isoformat()] + sid_params
                    cursor.execute(f"SELECT v.*, u.username as staff_name FROM violation v LEFT JOIN \"user\" u ON v.staff_id = u.id WHERE v.class_id = %s AND v.date >= %s AND v.date <= %s AND v.student_id IN ({placeholders}) ORDER BY v.created_at DESC", tuple(params_all))
                    all_rows = cursor.fetchall()
                    for ar in all_rows:
                        sid = ar['student_id']
                        viol_list_by_student.setdefault(sid, []).append(dict(ar))
                except Exception:
                    viol_list_by_student = {}

        if request.method == 'GET':
            return render_template('teacher_assign_violation.html', classes=classes, students=students, violation_types=violation_types, sel_class=sel_class, viol_by_student=viol_by_student, viol_list_by_student=viol_list_by_student, default_date=default_date)

        # POST: handle assignments
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token','danger')
            return redirect(request.referrer or url_for('teacher_dashboard'))

        class_id = request.form.get('class_id')
        student_ids = request.form.getlist('student_id')
        if not student_ids:
            single = request.form.get('student_id')
            if single:
                student_ids = [single]

        date_val = request.form.get('date') or default_date
        inserted = 0
        skipped = []
        for sid in student_ids:
            sid_str = str(sid)
            v_name = request.form.get(f'violation_type_{sid_str}')
            lesson = request.form.get(f'lesson_{sid_str}')
            period = request.form.get(f'period_{sid_str}')
            if not v_name:
                skipped.append((sid, 'no violation'))
                continue
            try:
                # allow numeric id or name
                v_id_int = None
                try:
                    v_id_int = int(v_name)
                except Exception:
                    v_id_int = None

                violation_name = None
                if v_id_int:
                    cursor.execute('SELECT name FROM violation_type WHERE id = %s', (v_id_int,))
                    r = cursor.fetchone()
                    violation_name = r['name'] if r and 'name' in r else None
                else:
                    # v_name may be a name
                    cursor.execute('SELECT id, name FROM violation_type WHERE name = %s LIMIT 1', (v_name,))
                    r = cursor.fetchone()
                    if r and 'id' in r:
                        violation_name = r['name']
                    else:
                        violation_name = v_name

                cursor.execute('INSERT INTO violation (student_id, class_id, staff_id, violation_name, lesson_name, period, date) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id', (int(sid), int(class_id) if class_id else None, int(current_user.id), violation_name, lesson, int(period) if period else None, date_val))
                ir = cursor.fetchone()
                vid = ir['id'] if ir and 'id' in ir else None
                try:
                    details = json.dumps({'violation_name': violation_name, 'lesson': lesson, 'period': period})
                    cursor.execute('INSERT INTO violation_audit (violation_id, action, user_id, username, details) VALUES (%s,%s,%s,%s,%s)', (vid, 'create', current_user.id, getattr(current_user, 'username', None), details))
                except Exception:
                    pass
                inserted += 1
            except Exception as ex:
                try:
                    conn.rollback()
                except Exception:
                    pass
                skipped.append((sid, str(ex)))

        if inserted:
            try:
                conn.commit()
            except Exception:
                pass
            flash(f'Assigned violation for {inserted} students','success')
        if skipped:
            flash(f'Skipped {len(skipped)} students','warning')
        return redirect(request.referrer or url_for('teacher_assign_violation'))
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        flash(f'Error assigning violation: {e}','danger')
        return redirect(request.referrer or url_for('teacher_dashboard'))

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
    
    # Get date from query parameter or use today
    from datetime import datetime
    date_param = request.args.get('date')
    if date_param:
        try:
            # Parse the date from the form
            selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except:
            selected_date = get_current_date()
    else:
        selected_date = get_current_date()
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, s.name as student_name, c.name as class_name, u.username as teacher_name
            FROM attendance a
            LEFT JOIN student s ON a.student_id = s.id
            LEFT JOIN school_class c ON a.class_id = c.id
            LEFT JOIN "user" u ON a.teacher_id = u.id
            WHERE a.date = %s
            ORDER BY c.name, a.period
            LIMIT 500
        """, (selected_date,))
        attendance_rows = cursor.fetchall()
        records = [RowObject(dict(r)) for r in attendance_rows]
    except Exception as e:
        print(f"Error loading attendance: {e}")
        records = []
    
    return render_template('admin_attendance.html', records=records, today=selected_date)


@app.route('/admin/violations')
@login_required
def admin_violations():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    try:
        conn = get_db()
        cursor = conn.cursor()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)

        # filters
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)

        where = []
        params = []
        if student_id:
            where.append('v.student_id = %s')
            params.append(student_id)
        if class_id:
            where.append('v.class_id = %s')
            params.append(class_id)

        where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''

        # total
        cursor.execute(f"SELECT COUNT(*) as cnt FROM violation v {where_sql}", tuple(params))
        total = cursor.fetchone()['cnt'] if cursor.rowcount != 0 else 0

        offset = (page - 1) * per_page
        cursor.execute(
            f"SELECT v.*, s.name as student_name, c.name as class_name, u.username as staff_username, u.username as staff_name FROM violation v LEFT JOIN student s ON v.student_id = s.id LEFT JOIN school_class c ON v.class_id = c.id LEFT JOIN \"user\" u ON v.staff_id = u.id {where_sql} ORDER BY v.created_at DESC LIMIT %s OFFSET %s",
            tuple(params) + (per_page, offset)
        )
        rows = cursor.fetchall()
        violations = [RowObject(dict(r)) for r in rows]

        pagination = {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page if per_page else 1}

        return render_template('admin_violations.html', violations=violations, pagination=pagination)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Error loading admin violations: {e}\n{tb}")
        try:
            with open('/tmp/admin_violations_trace.log','a') as fh:
                fh.write('\n---\n')
                fh.write(tb)
        except Exception:
            pass

        # show traceback inline to admins for debugging
        if current_user.is_authenticated and getattr(current_user, 'role', None) == 'admin':
            return render_template('admin_violations_error.html', error=tb), 500

        flash('Error loading violations', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/violations/export_xlsx')
@login_required
def admin_export_violations_xlsx():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT v.*, s.name as student_name, s.roll_number as student_roll_number, c.name as class_name, u.username as staff_username
            FROM violation v
            LEFT JOIN student s ON v.student_id = s.id
            LEFT JOIN school_class c ON v.class_id = c.id
            LEFT JOIN "user" u ON v.staff_id = u.id
            ORDER BY COALESCE(c.name, ''), v.created_at
            """
        )
        rows = cursor.fetchall()

        grouped = {}
        for r in rows:
            cls = r.get('class_name') or 'Unassigned'
            grouped.setdefault(cls, []).append(r)

        wb = Workbook()
        # remove default sheet
        try:
            wb.remove(wb.active)
        except Exception:
            pass

        def safe_sheet_name(name):
            bad = '[]:*?/\\'
            for ch in bad:
                name = name.replace(ch, '-')
            return name[:31] or 'Sheet'

        headers = ['ID','Student','Student National ID','Violation','Lesson','Period','Date','Recorded At','By','Statement','Parental Consent','Referral']
        from datetime import datetime, date, time
        def _norm(v):
            if isinstance(v, (datetime, date, time)):
                try:
                    return v.isoformat()
                except Exception:
                    return str(v)
            return v

        for cls_name, items in grouped.items():
            sheet = wb.create_sheet(title=safe_sheet_name(cls_name))
            sheet.append([cls_name])
            sheet.append(headers)
            for r in items:
                sheet.append([
                    _norm(r.get('id')),
                    _norm(r.get('student_name') or r.get('student_id')),
                    _norm(r.get('student_roll_number')),
                    _norm(r.get('violation_name')),
                    _norm(r.get('lesson_name')),
                    _norm(r.get('period')),
                    _norm(r.get('date')),
                    _norm(r.get('created_at')),
                    _norm(r.get('staff_username')),
                    _norm(r.get('statement_of_receipt')),
                    _norm(r.get('parental_consent')),
                    _norm(r.get('referral')),
                ])

        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        return send_file(bio, as_attachment=True, download_name='violations_by_class.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('/tmp/admin_violations_export_trace.log','a') as fh:
                fh.write('\n---\n')
                fh.write(tb)
        except Exception:
            pass
        flash('Error exporting violations', 'danger')
        return redirect(url_for('admin_violations'))


@app.route('/admin/violation_audit')
@login_required
def admin_violation_audit():
        if current_user.role != 'admin':
            flash('Unauthorized', 'danger')
            return redirect(url_for('index'))

        try:
            conn = get_db()
            cursor = conn.cursor()

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 25, type=int)

            cursor.execute('SELECT COUNT(*) as cnt FROM violation_audit')
            total = cursor.fetchone()['cnt'] if cursor.rowcount else 0
            offset = (page - 1) * per_page

            cursor.execute('SELECT va.*, u.username as user_username FROM violation_audit va LEFT JOIN "user" u ON va.user_id = u.id ORDER BY va.created_at DESC LIMIT %s OFFSET %s', (per_page, offset))
            rows = cursor.fetchall()
            audits = [RowObject(dict(r)) for r in rows]

            pagination = {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page if per_page else 1}

            return render_template('admin_violation_audit.html', audits=audits, pagination=pagination)
        except Exception as e:
            print(f"Error loading audit logs: {e}")
            flash('Error loading audit logs', 'danger')
            return redirect(url_for('admin_dashboard'))

# ================ Violation Types (Admin CRUD) ================
@app.route('/admin/violation_types')
@login_required
def admin_violation_types():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        # ensure table exists

        cursor.execute('SELECT id, name, status, created_at, updated_at FROM violation_type ORDER BY name')
        rows = cursor.fetchall()
        types = [RowObject(dict(r)) for r in rows]
        return render_template('admin_violation_types.html', types=types)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Error loading violation types: {e}\n{tb}")
        try:
            with open('/tmp/admin_violation_types_trace.log', 'a') as fh:
                fh.write('\n---\n')
                fh.write(tb)
        except Exception:
            pass
        flash('Error loading violation types', 'danger')
        # If admin, show traceback inline to help debugging
        if current_user.is_authenticated and getattr(current_user, 'role', None) == 'admin':
            return render_template('admin_violations_error.html', error=tb), 500
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/performance_levels')
@login_required
def admin_performance_levels():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        conn = get_db()
        cursor = conn.cursor()
   
        cursor.execute('SELECT id, name, status, created_at, updated_at FROM performance_level ORDER BY name')
        rows = cursor.fetchall()
        types = [RowObject(dict(r)) for r in rows]
        return render_template('admin_performance_levels.html', types=types)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('/tmp/admin_performance_levels_trace.log','a') as fh:
                fh.write('\n---\n')
                fh.write(tb)
        except Exception:
            pass
        print(f"Error loading performance levels: {e}")
        flash('Error loading performance levels', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/performance', methods=['GET'])
@login_required
def admin_performance():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    conn = get_db(); cursor = conn.cursor()
    

    # filter by year/week optional
    year = request.args.get('year', type=int)
    week = request.args.get('week', type=int)

    params = []
    where = ''
    if year:
        where += ' AND p.year = %s'
        params.append(year)
    if week:
        where += ' AND p.week_number = %s'
        params.append(week)

    # fetch grouped by week_number, year, teacher
    sql = (
        "SELECT p.year, p.week_number, p.teacher_id, u.username as teacher_name, c.name as class_name, s.name as student_name, p.level_name, p.comment "
        "FROM performance p LEFT JOIN \"user\" u ON p.teacher_id = u.id LEFT JOIN school_class c ON p.class_id = c.id LEFT JOIN student s ON p.student_id = s.id "
        f"WHERE 1=1 {where} ORDER BY p.year DESC, p.week_number DESC, u.username, c.name, s.name LIMIT 2000"
    )
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()

    # organize by (year, week)
    grouped = {}
    for r in rows:
        key = (r['year'], r['week_number'])
        grouped.setdefault(key, []).append(RowObject(dict(r)))

    return render_template('admin_performance.html', grouped=grouped, rows=rows)


@app.route('/admin/performance/export', methods=['GET'])
@login_required
def admin_performance_export():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    conn = get_db(); cursor = conn.cursor()
    year = request.args.get('year', type=int)
    week = request.args.get('week', type=int)

    params = []
    where = ''
    fname_suffix = 'all_weeks'
    if year:
        where += ' AND p.year = %s'
        params.append(year)
        fname_suffix = f'Y{year}'
    if week:
        where += ' AND p.week_number = %s'
        params.append(week)
        fname_suffix = f'W{week}_' + fname_suffix

    sql = (
        "SELECT p.year, p.week_number, u.username as teacher_name, c.name as class_name, s.name as student_name, p.level_name, p.comment "
        "FROM performance p LEFT JOIN \"user\" u ON p.teacher_id = u.id LEFT JOIN school_class c ON p.class_id = c.id LEFT JOIN student s ON p.student_id = s.id "
        f"WHERE 1=1 {where} ORDER BY p.year DESC, p.week_number DESC, u.username, c.name, s.name"
    )
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()

    # create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Performance'
    headers = ['Year','Week','Teacher','Class','Student','Level','Comment']
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = h

    r = 2
    for row in rows:
        ws.cell(row=r, column=1).value = row['year']
        ws.cell(row=r, column=2).value = row['week_number']
        ws.cell(row=r, column=3).value = row.get('teacher_name')
        ws.cell(row=r, column=4).value = row.get('class_name')
        ws.cell(row=r, column=5).value = row.get('student_name')
        ws.cell(row=r, column=6).value = row.get('level_name')
        ws.cell(row=r, column=7).value = row.get('comment')
        r += 1

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f'performance_{fname_suffix}.xlsx'
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)


@app.route('/admin/performance_levels/create', methods=['GET','POST'])
@login_required
def admin_performance_level_create():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db(); cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_level (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            status VARCHAR(32) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    ''')
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        status = request.form.get('status') or 'active'
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(url_for('admin_performance_levels'))
        if not name:
            flash('Name required', 'danger')
            return render_template('admin_performance_level_form.html', type=None)
        try:
            cursor.execute('INSERT INTO performance_level (name, status) VALUES (%s,%s) RETURNING id', (name,status))
            conn.commit()
            flash('Performance level created','success')
            return redirect(url_for('admin_performance_levels'))
        except Exception as e:
            conn.rollback()
            flash(f'Error creating level: {e}','danger')
            return render_template('admin_performance_level_form.html', type=None)
    return render_template('admin_performance_level_form.html', type=None)


@app.route('/admin/performance_levels/<int:pid>/edit', methods=['GET','POST'])
@login_required
def admin_performance_level_edit(pid):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db(); cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_level (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            status VARCHAR(32) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    ''')
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(url_for('admin_performance_levels'))
        name = (request.form.get('name') or '').strip()
        status = request.form.get('status') or 'active'
        if not name:
            flash('Name required','danger')
            return redirect(url_for('admin_performance_level_edit', pid=pid))
        try:
            cursor.execute('UPDATE performance_level SET name=%s, status=%s, updated_at=NOW() WHERE id=%s', (name,status,pid))
            conn.commit()
            flash('Updated','success')
            return redirect(url_for('admin_performance_levels'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating: {e}','danger')
    cursor.execute('SELECT * FROM performance_level WHERE id=%s',(pid,))
    row = cursor.fetchone()
    if not row:
        flash('Not found','warning'); return redirect(url_for('admin_performance_levels'))
    return render_template('admin_performance_level_form.html', type=RowObject(dict(row)))


@app.route('/admin/performance_levels/<int:pid>/delete', methods=['POST'])
@login_required
def admin_performance_level_delete(pid):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        flash('Invalid CSRF token', 'danger')
        return redirect(url_for('admin_performance_levels'))
    try:
        conn = get_db(); cursor = conn.cursor()
        # ensure performance table and unique index exist before INSERT with ON CONFLICT
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER,
                    class_id INTEGER,
                    teacher_id INTEGER,
                    week_number INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    level_id INTEGER,
                    level_name TEXT,
                    comment TEXT,
                    status VARCHAR(32) DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
        except Exception:
            pass
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS performance_unique_idx ON performance (student_id, teacher_id, week_number)')
        except Exception:
            pass
        # Trace incoming form for debugging
        try:
            with open('/tmp/admin_performance_assign_trace.log','a') as fh:
                fh.write('\n--- POST /teacher/assign_performance ---\n')
                for k, v in request.form.items():
                    fh.write(f"{k}={v}\n")
                fh.write('lists:\n')
                for k in request.form.keys():
                    vals = request.form.getlist(k)
                    if len(vals) > 1:
                        fh.write(f"{k} -> {vals}\n")
        except Exception:
            pass
        cursor.execute('DELETE FROM performance_level WHERE id=%s',(pid,))
        conn.commit()
        flash('Deleted','success')
    except Exception as e:
        conn.rollback(); flash(f'Error deleting: {e}','danger')
    return redirect(url_for('admin_performance_levels'))


@app.route('/admin/performance')
@login_required
def admin_performance_list():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        conn = get_db(); cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                class_id INTEGER,
                teacher_id INTEGER,
                week_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                level_id INTEGER,
                level_name TEXT,
                comment TEXT,
                status VARCHAR(32) DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        # ensure uniqueness to prevent duplicate records per student/teacher/week
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS performance_unique_idx ON performance (student_id, teacher_id, week_number)')
        except Exception:
            pass
        cursor.execute('SELECT p.*, s.name as student_name, c.name as class_name, u.username as teacher_name FROM performance p LEFT JOIN student s ON p.student_id = s.id LEFT JOIN school_class c ON p.class_id = c.id LEFT JOIN "user" u ON p.teacher_id = u.id ORDER BY p.year DESC, p.week_number DESC LIMIT 500')
        rows = cursor.fetchall(); items = [RowObject(dict(r)) for r in rows]
        return render_template('admin_performance.html', items=items)
    except Exception as e:
        tb = traceback.format_exc(); print(tb)
        flash('Error loading performance','danger'); return redirect(url_for('admin_dashboard'))


@app.route('/teacher/assign_performance', methods=['GET','POST'])
@login_required
def teacher_assign_performance():
    if current_user.role != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    try:
        # GET: show form
        if request.method == 'GET':
            conn = get_db(); cursor = conn.cursor()
            # Fetch classes assigned to this teacher from the user's `classes` column
            cursor.execute('SELECT classes FROM "user" WHERE id = %s', (current_user.id,))
            user_row = cursor.fetchone()
            classes = []
            if user_row and user_row.get('classes'):
                class_ids_str = user_row['classes'].strip()
                if class_ids_str:
                    class_ids = [cid.strip() for cid in class_ids_str.split(',') if cid.strip()]
                    if class_ids:
                        placeholders = ','.join(['%s'] * len(class_ids))
                        cursor.execute(f"SELECT id, name FROM school_class WHERE id IN ({placeholders}) ORDER BY name", class_ids)
                        classes = cursor.fetchall()

            # performance levels
            # Ensure performance_level table exists (runtime guard)
            
            cursor.execute('SELECT id, name FROM performance_level WHERE status = %s ORDER BY name', ('active',))
            levels = cursor.fetchall()
            # optional selected class to list students
            sel_class = request.args.get('class_id')
            students = []
            perf_by_student = {}
            perf_list_by_student = {}
            if sel_class:
                cursor.execute('SELECT id, name, roll_number FROM student WHERE class_id = %s ORDER BY roll_number NULLS LAST, name', (int(sel_class),))
                students = cursor.fetchall()
                # default week_number = current ISO week number (used to load existing assignments)
                from datetime import date
                today = date.today()
                try:
                    iso = today.isocalendar()
                    default_week_number = iso[1]
                    default_year = iso[0]
                except Exception:
                    default_week_number = int(today.strftime('%V')) if hasattr(today, 'strftime') else 1
                    default_year = today.year

                # Ensure performance table exists (runtime guard) and load existing assignments
                try:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS performance (
                            id SERIAL PRIMARY KEY,
                            student_id INTEGER,
                            class_id INTEGER,
                            teacher_id INTEGER,
                            week_number INTEGER NOT NULL,
                            year INTEGER NOT NULL,
                            level_id INTEGER,
                            level_name TEXT,
                            comment TEXT,
                            status VARCHAR(32) DEFAULT 'active',
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        )
                    ''')
                except Exception:
                    pass
                try:
                    student_ids = [str(s['id']) for s in students]
                    perf_by_student = {}
                    perf_list_by_student = {}
                    if student_ids:
                        placeholders = ','.join(['%s'] * len(student_ids))
                        # convert student ids to ints
                        sid_params = [int(x) for x in student_ids]

                        # 1) load assignments made by the current teacher (used to prefill the form)
                        try:
                            params = [int(sel_class), int(default_week_number), int(default_year), int(current_user.id)] + sid_params
                            cursor.execute(f"SELECT * FROM performance WHERE class_id = %s AND week_number = %s AND year = %s AND teacher_id = %s AND student_id IN ({placeholders})", tuple(params))
                            prow = cursor.fetchall()
                            for pr in prow:
                                perf_by_student[pr['student_id']] = dict(pr)
                        except Exception:
                            perf_by_student = {}

                        # 2) load ALL performances for those students for the same week/year (include teacher name)
                        try:
                            params_all = [int(sel_class), int(default_week_number), int(default_year)] + sid_params
                            cursor.execute(f"SELECT p.*, u.username as teacher_name FROM performance p LEFT JOIN \"user\" u ON p.teacher_id = u.id WHERE p.class_id = %s AND p.week_number = %s AND p.year = %s AND p.student_id IN ({placeholders}) ORDER BY p.created_at DESC", tuple(params_all))
                            all_rows = cursor.fetchall()
                            for ar in all_rows:
                                sid = ar['student_id']
                                perf_list_by_student.setdefault(sid, []).append(dict(ar))
                        except Exception:
                            perf_list_by_student = {}
                except Exception:
                    perf_by_student = {}
            # default week_number = current ISO week number
            from datetime import date
            today = date.today()
            try:
                iso = today.isocalendar()
                default_week_number = iso[1]
                default_year = iso[0]
            except Exception:
                # fallback
                default_week_number = int(today.strftime('%V')) if hasattr(today, 'strftime') else 1
                default_year = today.year
            return render_template('teacher_assign_performance.html', classes=classes, students=students, levels=levels, default_week_number=default_week_number, default_year=default_year, sel_class=sel_class, perf_by_student=perf_by_student, perf_list_by_student=perf_list_by_student)

        # POST: accept single or bulk assignments
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token','danger')
            return redirect(request.referrer or url_for('teacher_dashboard'))

        conn = get_db(); cursor = conn.cursor()
        week_number_raw = (request.form.get('week_number') or '').strip()
        year_raw = (request.form.get('year') or '').strip()

        # Normalize week_number and year into integers. Support cases where week_number
        # is submitted as a date string (legacy), or as the ISO week number.
        from datetime import date, datetime
        try:
            if week_number_raw and '-' in week_number_raw:
                # submitted a date (e.g. week_start); convert to ISO week
                dt = datetime.fromisoformat(week_number_raw).date()
                week_number = dt.isocalendar()[1]
                year = dt.isocalendar()[0]
            else:
                week_number = int(week_number_raw) if week_number_raw else None
                year = int(year_raw) if year_raw else None
        except Exception:
            # fallback to current week/year
            today = date.today()
            iso = today.isocalendar()
            week_number = iso[1]
            year = iso[0]
        class_id = request.form.get('class_id')

        student_ids = request.form.getlist('student_id')
        # support either repeated student_id or a single value
        if not student_ids:
            single_id = request.form.get('student_id')
            if single_id:
                student_ids = [single_id]

        if not student_ids or not week_number:
            # log form for debugging
            try:
                with open('/tmp/admin_performance_assign_trace.log','a') as fh:
                    fh.write('\n--- Missing fields on POST /teacher/assign_performance ---\n')
                    for k in request.form.keys():
                        fh.write(f"FORM {k}={request.form.get(k)}\n")
            except Exception:
                pass
            flash('Missing fields','danger')
            return redirect(request.referrer or url_for('teacher_dashboard'))

        # Prefer per-student fields like level_id_<student_id> and comment_<student_id>
        level_ids = request.form.getlist('level_id')
        comments = request.form.getlist('comment')

        entries = []
        for idx, sid in enumerate(student_ids):
            sid_str = str(sid)
            # check per-student fields first
            lid = request.form.get(f'level_id_{sid_str}')
            comm = request.form.get(f'comment_{sid_str}')
            # fallback to parallel arrays if per-student missing
            if not lid:
                if idx < len(level_ids):
                    lid = level_ids[idx]
                else:
                    lid = ''
            if comm is None:
                if idx < len(comments):
                    comm = comments[idx]
                else:
                    comm = ''
            entries.append((sid, lid, comm))

        inserted = 0
        deleted = 0
        skipped = []
        for sid, lid, comm in entries:
            if not lid:
                # If teacher cleared the select, delete any existing assignment for this student/week
                try:
                    cursor.execute('DELETE FROM performance WHERE student_id=%s AND teacher_id=%s AND week_number=%s AND year=%s', (int(sid), int(current_user.id), int(week_number), int(year)))
                    if cursor.rowcount and cursor.rowcount > 0:
                        deleted += cursor.rowcount
                    else:
                        skipped.append((sid, 'no level'))
                except Exception as ex_del:
                    # record delete error and continue
                    try:
                        with open('/tmp/admin_performance_assign_trace.log','a') as fh:
                            fh.write('--- Error deleting performance ---\n')
                            fh.write(f"student={sid} teacher_id={current_user.id} week_number={week_number} year={year} Exception: {ex_del}\n")
                    except Exception:
                        pass
                    skipped.append((sid, f'delete error: {ex_del}'))
                continue
            level_name = None
            lid_int = None
            # try numeric id first
            try:
                lid_int = int(lid)
            except Exception:
                lid_int = None
            try:
                if lid_int:
                    cursor.execute('SELECT name FROM performance_level WHERE id=%s', (lid_int,))
                    lr = cursor.fetchone()
                    level_name = lr['name'] if lr and 'name' in lr else None
                else:
                    # maybe lid contains the level name; try to find id by name
                    cursor.execute('SELECT id, name FROM performance_level WHERE name = %s LIMIT 1', (lid,))
                    lr = cursor.fetchone()
                    if lr and 'id' in lr:
                        lid_int = lr['id']
                        level_name = lr['name']
                    else:
                        # treat lid as level_name directly
                        level_name = lid

                if not lid_int and not level_name:
                    skipped.append((sid, f'invalid level ({lid})'))
                    continue

                # ensure year/week are ints (computed earlier). Use these normalized values.
                # Perform UPDATE first; if no row updated, INSERT. This avoids relying on ON CONFLICT and a unique index.
                try:
                    cursor.execute(
                        'UPDATE performance SET level_id=%s, level_name=%s, comment=%s, updated_at=NOW() WHERE student_id=%s AND teacher_id=%s AND week_number=%s',
                        (int(lid_int) if lid_int else None, level_name, comm, int(sid), int(current_user.id), int(week_number))
                    )
                    if cursor.rowcount == 0:
                        cursor.execute(
                            'INSERT INTO performance (student_id, class_id, teacher_id, week_number, year, level_id, level_name, comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                            (int(sid), int(class_id) if class_id else None, int(current_user.id), int(week_number), int(year), int(lid_int) if lid_int else None, level_name, comm)
                        )
                    inserted += 1
                except Exception:
                    raise
            except Exception as ex:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    with open('/tmp/admin_performance_assign_trace.log','a') as fh:
                        fh.write('--- Error inserting performance ---\n')
                        fh.write(f"student={sid} class_id={class_id} week_number_raw={week_number_raw} year_raw={year_raw} normalized_week={week_number} normalized_year={year} level_in={lid} level_id={lid_int} level_name={level_name} comment={comm}\n")
                        fh.write(f"Exception: {ex}\n")
                        # dump full form keys for debugging
                        try:
                            for k in request.form.keys():
                                fh.write(f"FORM {k}={request.form.get(k)}\n")
                        except Exception:
                            pass
                except Exception:
                    pass
        if inserted or deleted:
            try:
                conn.commit()
            except Exception:
                pass
            if inserted:
                flash(f'Assigned performance for {inserted} students','success')
            if deleted:
                flash(f'Deleted performance for {deleted} students','info')
            if skipped:
                flash(f'Skipped {len(skipped)} students (no level provided)','warning')
        else:
            # log skipped details and form for debugging
            try:
                with open('/tmp/admin_performance_assign_trace.log','a') as fh:
                    fh.write('\n--- No performance assignments made (skipped) ---\n')
                    fh.write(f'Skipped entries: {skipped}\n')
                    for k in request.form.keys():
                        fh.write(f"FORM {k}={request.form.get(k)}\n")
            except Exception:
                pass
            flash('No performance assignments made','warning')
        return redirect(request.referrer or url_for('teacher_dashboard'))
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        flash(f'Error assigning performance: {e}','danger')
        return redirect(request.referrer or url_for('teacher_dashboard'))


@app.route('/admin/violation_types/create', methods=['GET', 'POST'])
@login_required
def admin_violation_type_create():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db()
    cursor = conn.cursor()
    # ensure table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violation_type (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            status VARCHAR(32) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    ''')
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        status = request.form.get('status') or 'active'
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(url_for('admin_violation_types'))
        if not name:
            flash('Name is required', 'danger')
            return render_template('admin_violation_type_form.html', type=None)
        try:
            cursor.execute('INSERT INTO violation_type (name, status) VALUES (%s,%s) RETURNING id', (name, status))
            conn.commit()
            flash('Violation type created', 'success')
            return redirect(url_for('admin_violation_types'))
        except Exception as e:
            conn.rollback()
            flash(f'Error creating type: {e}', 'danger')
            return render_template('admin_violation_type_form.html', type=None)
    return render_template('admin_violation_type_form.html', type=None)


@app.route('/admin/violation_types/<int:vt_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_violation_type_edit(vt_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    conn = get_db()
    cursor = conn.cursor()
    # ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violation_type (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            status VARCHAR(32) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    ''')
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(url_for('admin_violation_types'))
        name = (request.form.get('name') or '').strip()
        status = request.form.get('status') or 'active'
        if not name:
            flash('Name is required', 'danger')
            return redirect(url_for('admin_violation_type_edit', vt_id=vt_id))
        try:
            cursor.execute('UPDATE violation_type SET name=%s, status=%s, updated_at=NOW() WHERE id=%s', (name, status, vt_id))
            conn.commit()
            flash('Violation type updated', 'success')
            return redirect(url_for('admin_violation_types'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating type: {e}', 'danger')
    # GET
    cursor.execute('SELECT * FROM violation_type WHERE id = %s', (vt_id,))
    row = cursor.fetchone()
    if not row:
        flash('Violation type not found', 'warning')
        return redirect(url_for('admin_violation_types'))
    vt = RowObject(dict(row))
    return render_template('admin_violation_type_form.html', type=vt)


@app.route('/admin/violation_types/<int:vt_id>/delete', methods=['POST'])
@login_required
def admin_violation_type_delete(vt_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        flash('Invalid CSRF token', 'danger')
        return redirect(url_for('admin_violation_types'))
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM violation_type WHERE id = %s', (vt_id,))
        conn.commit()
        flash('Violation type deleted', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting type: {e}', 'danger')
    return redirect(url_for('admin_violation_types'))


@app.route('/admin/violations/<int:viol_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_violation(viol_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        # CSRF
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            flash('Invalid CSRF token', 'danger')
            return redirect(url_for('admin_violations'))
        try:
            violation_name = request.form.get('violation_name')
            lesson_name = request.form.get('lesson_name')
            period = request.form.get('period')
            statement_of_receipt = request.form.get('statement_of_receipt')
            parental_consent = request.form.get('parental_consent')
            referral = request.form.get('referral')

            # basic validation
            if parental_consent and parental_consent not in ('consent','refusal'):
                flash('Invalid parental consent value', 'danger')
                return redirect(url_for('admin_edit_violation', viol_id=viol_id))

            # record old values
            cursor.execute('SELECT * FROM violation WHERE id = %s', (viol_id,))
            old = cursor.fetchone()

            cursor.execute("""
                UPDATE violation SET violation_name = %s, lesson_name = %s, period = %s, statement_of_receipt = %s, parental_consent = %s, referral = %s WHERE id = %s
            """, (violation_name, lesson_name, int(period) if period else None, statement_of_receipt, parental_consent, referral, viol_id))
            # insert audit record describing changes
            try:
                new = {'violation_name': violation_name, 'lesson_name': lesson_name, 'period': period, 'statement_of_receipt': statement_of_receipt, 'parental_consent': parental_consent, 'referral': referral}
                details = {'old': dict(old) if old else {}, 'new': new}
                cursor.execute('INSERT INTO violation_audit (violation_id, action, user_id, username, details) VALUES (%s,%s,%s,%s,%s)', (viol_id, 'edit', current_user.id, getattr(current_user,'username',None), json.dumps(details)))
            except Exception:
                pass

            conn.commit()
            flash('Violation updated', 'success')
            return redirect(url_for('admin_violations'))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating violation: {e}', 'danger')

    # GET
    cursor.execute('SELECT * FROM violation WHERE id = %s', (viol_id,))
    row = cursor.fetchone()
    if not row:
        flash('Violation not found', 'warning')
        return redirect(url_for('admin_violations'))
    viol = RowObject(dict(row))
    return render_template('admin_violation_form.html', viol=viol)


@app.route('/admin/violations/<int:viol_id>/delete', methods=['POST'])
@login_required
def admin_delete_violation(viol_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    # CSRF
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        flash('Invalid CSRF token', 'danger')
        return redirect(url_for('admin_violations'))

    try:
        conn = get_db()
        cursor = conn.cursor()
        # fetch row for audit
        cursor.execute('SELECT * FROM violation WHERE id = %s', (viol_id,))
        row = cursor.fetchone()
        try:
            cursor.execute('INSERT INTO violation_audit (violation_id, action, user_id, username, details) VALUES (%s,%s,%s,%s,%s)', (viol_id, 'delete', current_user.id, getattr(current_user,'username',None), json.dumps({'old': dict(row) if row else {}})))
        except Exception:
            pass
        cursor.execute('DELETE FROM violation WHERE id = %s', (viol_id,))
        conn.commit()
        flash('Violation deleted', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting violation: {e}', 'danger')

    return redirect(url_for('admin_violations'))

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
        roll_number = request.form.get('roll_number')
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
                'INSERT INTO "user" (username, password, role, email, roll_number, classes) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                (username, hashed_pw, role, email, roll_number, classes_string)
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
        #roll_number = request.form.get('roll_number')
        email = request.form.get('email')
        assigned_classes = request.form.getlist('assigned_classes')
        
        try:
            # Prepare classes string
            classes_string = ','.join(assigned_classes) if assigned_classes else None
            
            # Update user
            if password:
                hashed_pw = generate_password_hash(password, method='scrypt')
                cursor.execute(
                    'UPDATE "user" SET username = %s, role = %s, password = %s, email = %s, classes = %s WHERE id = %s',
                    (username, role, hashed_pw, email, classes_string, user_id)
                )
            else:
                cursor.execute(
                    'UPDATE "user" SET username = %s, role = %s, email = %s,classes = %s WHERE id = %s',
                    (username, role, email, classes_string, user_id)
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

# ================ Staff Students Routes ================

@app.route('/staff/students', methods=['GET', 'POST'])
@login_required
def staff_students():
    if current_user.role not in ['admin', 'staff']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all classes
    try:
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    students_by_class = {}
    selected_class_id = request.args.get('class_id', type=int)
    
    # If class is selected, fetch students for that class
    if selected_class_id:
        try:
            cursor.execute("""
                SELECT s.* FROM student s
                WHERE s.class_id = %s
                ORDER BY s.name
            """, (selected_class_id,))
            students_rows = cursor.fetchall()
            students_by_class[selected_class_id] = [RowObject(dict(r)) for r in students_rows]
        except Exception as e:
            print(f"Error fetching students: {e}")
            students_by_class[selected_class_id] = []
    else:
        # Get all students grouped by class
        try:
            cursor.execute("""
                SELECT s.*, c.name as class_name FROM student s
                LEFT JOIN school_class c ON s.class_id = c.id
                ORDER BY c.name, s.name
            """)
            students_rows = cursor.fetchall()
            for student_row in students_rows:
                student_obj = RowObject(dict(student_row))
                class_id = student_obj.class_id
                if class_id not in students_by_class:
                    students_by_class[class_id] = []
                students_by_class[class_id].append(student_obj)
        except:
            students_by_class = {}
    
    return render_template('staff_students.html', 
                         classes=classes, 
                         students_by_class=students_by_class,
                         selected_class_id=selected_class_id)

@app.route('/staff/students/<int:student_id>/update-phone', methods=['POST'])
@login_required
def staff_update_student_phone(student_id):
    if current_user.role not in ['admin', 'staff']:
        return {'success': False, 'message': 'Unauthorized'}, 403
    
    try:
        phone1 = request.form.get('phone1', '').strip()
        phone2 = request.form.get('phone2', '').strip()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Update student phone numbers
        cursor.execute("""
            UPDATE student 
            SET phone1 = %s, phone2 = %s
            WHERE id = %s
        """, (phone1 if phone1 else None, phone2 if phone2 else None, student_id))
        
        conn.commit()
        
        flash(f'Phone numbers updated successfully', 'success')
        return redirect(request.referrer or url_for('staff_students'))
    except Exception as e:
        conn.rollback()
        flash(f'Error updating phone numbers: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('staff_students'))

@app.route('/staff/students/export-excel', methods=['GET'])
@login_required
def staff_export_students_excel():
    if current_user.role not in ['admin', 'staff']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    selected_class_id = request.args.get('class_id', type=int)
    
    if not selected_class_id:
        flash('Please select a class first', 'warning')
        return redirect(url_for('staff_students'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get class name
        cursor.execute("SELECT name FROM school_class WHERE id = %s", (selected_class_id,))
        class_row = cursor.fetchone()
        class_name = class_row['name'] if class_row else 'Students'
        
        # Get students for the selected class
        cursor.execute("""
            SELECT s.id, s.name, s.roll_number, s.phone1, s.phone2, c.name as class_name
            FROM student s
            LEFT JOIN school_class c ON s.class_id = c.id
            WHERE s.class_id = %s
            ORDER BY s.name
        """, (selected_class_id,))
        students_rows = cursor.fetchall()
        
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Students"
        
        # Set up header row with styling
        headers = ['ID', 'Student Name', 'National ID', 'Phone 1', 'Phone 2', 'Class']
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add data rows
        for row_num, student_row in enumerate(students_rows, 2):
            ws.cell(row=row_num, column=1, value=student_row['id'])
            ws.cell(row=row_num, column=2, value=student_row['name'])
            ws.cell(row=row_num, column=3, value=student_row['roll_number'])
            ws.cell(row=row_num, column=4, value=student_row['phone1'])
            ws.cell(row=row_num, column=5, value=student_row['phone2'])
            ws.cell(row=row_num, column=6, value=student_row['class_name'])
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 20
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Return the file
        filename = f"{class_name}_students_{get_current_date()}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error exporting Excel: {e}")
        flash(f'Error exporting Excel: {str(e)}', 'danger')
        return redirect(url_for('staff_students'))

# ================ Public Students Routes (No Login Required) ================

@app.route('/manage-students', methods=['GET', 'POST'])
def manage_students():
    """Public page to view and manage students without login"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all classes
    try:
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except:
        classes = []
    
    students_by_class = {}
    selected_class_id = request.args.get('class_id', type=int)
    
    # If class is selected, fetch students for that class
    if selected_class_id:
        try:
            cursor.execute("""
                SELECT s.* FROM student s
                WHERE s.class_id = %s
                ORDER BY s.name
            """, (selected_class_id,))
            students_rows = cursor.fetchall()
            students_by_class[selected_class_id] = [RowObject(dict(r)) for r in students_rows]
        except Exception as e:
            print(f"Error fetching students: {e}")
            students_by_class[selected_class_id] = []
    else:
        # Get all students grouped by class
        try:
            cursor.execute("""
                SELECT s.*, c.name as class_name FROM student s
                LEFT JOIN school_class c ON s.class_id = c.id
                ORDER BY c.name, s.name
            """)
            students_rows = cursor.fetchall()
            for student_row in students_rows:
                student_obj = RowObject(dict(student_row))
                class_id = student_obj.class_id
                if class_id not in students_by_class:
                    students_by_class[class_id] = []
                students_by_class[class_id].append(student_obj)
        except:
            students_by_class = {}
    
    return render_template('manage_students.html', 
                         classes=classes, 
                         students_by_class=students_by_class,
                         selected_class_id=selected_class_id)

@app.route('/manage-students/<int:student_id>/update-phone', methods=['POST'])
def update_student_phone(student_id):
    """Update student phone numbers without login"""
    try:
        phone1 = request.form.get('phone1', '').strip()
        phone2 = request.form.get('phone2', '').strip()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Update student phone numbers
        cursor.execute("""
            UPDATE student 
            SET phone = %s, phone = %s
            WHERE id = %s
        """, (phone1 if phone1 else None, phone2 if phone2 else None, student_id))
        
        conn.commit()
        
        flash(f'Phone numbers updated successfully', 'success')
        return redirect(request.referrer or url_for('manage_students'))
    except Exception as e:
        conn.rollback()
        flash(f'Error updating phone numbers: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('manage_students'))

@app.route('/manage-students/export-excel', methods=['GET'])
def export_students_excel():
    """Export students to Excel without login"""
    selected_class_id = request.args.get('class_id', type=int)
    
    if not selected_class_id:
        flash('Please select a class first', 'warning')
        return redirect(url_for('manage_students'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get class name
        cursor.execute("SELECT name FROM school_class WHERE id = %s", (selected_class_id,))
        class_row = cursor.fetchone()
        class_name = class_row['name'] if class_row else 'Students'
        
        # Get students for the selected class
        cursor.execute("""
            SELECT s.id, s.name, s.roll_number, s.phone1, s.phone2, c.name as class_name
            FROM student s
            LEFT JOIN school_class c ON s.class_id = c.id
            WHERE s.class_id = %s
            ORDER BY s.name
        """, (selected_class_id,))
        students_rows = cursor.fetchall()
        
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Students"
        
        # Set up header row with styling
        headers = ['ID', 'Student Name', 'National ID', 'Phone 1', 'Phone 2', 'Class']
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add data rows
        for row_num, student_row in enumerate(students_rows, 2):
            ws.cell(row=row_num, column=1, value=student_row['id'])
            ws.cell(row=row_num, column=2, value=student_row['name'])
            ws.cell(row=row_num, column=3, value=student_row['roll_number'])
            ws.cell(row=row_num, column=4, value=student_row['phone1'])
            ws.cell(row=row_num, column=5, value=student_row['phone2'])
            ws.cell(row=row_num, column=6, value=student_row['class_name'])
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 20
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Return the file
        filename = f"{class_name}_students_{get_current_date()}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error exporting Excel: {e}")
        flash(f'Error exporting Excel: {str(e)}', 'danger')
        return redirect(url_for('manage_students'))

# ================ Attendance Tabs Routes (No Login Required) ================

def determine_current_period(periods_list):
    """Determine which period is currently active based on time"""
    from datetime import datetime
    current_time = datetime.now().time()
    
    for period in periods_list:
        # Handle both RowObject and dict formats
        start_time_val = period.get('start_time') if isinstance(period, dict) else getattr(period, 'start_time', None)
        end_time_val = period.get('end_time') if isinstance(period, dict) else getattr(period, 'end_time', None)
        period_num = period.get('period_num') if isinstance(period, dict) else getattr(period, 'period_num', None)
        
        if start_time_val and end_time_val:
            # Convert string times back to time objects if needed
            if isinstance(start_time_val, str):
                start_time_val = datetime.strptime(start_time_val, '%H:%M:%S').time()
            if isinstance(end_time_val, str):
                end_time_val = datetime.strptime(end_time_val, '%H:%M:%S').time()
            
            # Compare times
            if start_time_val <= current_time <= end_time_val:
                return period_num
    
    # If no period matches, return the first period
    if periods_list:
        first_period = periods_list[0]
        return first_period.get('period_num') if isinstance(first_period, dict) else getattr(first_period, 'period_num', None)
    
    return None

# ================ Public Attendance Routes (No Login Required) ================

@app.route('/attendance', methods=['GET', 'POST'])
def public_attendance():
    """Public page to record attendance without login - select class and teacher"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all classes and teachers
    try:
        cursor.execute("SELECT id, name FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [dict(r) for r in classes_rows]
        
        cursor.execute("SELECT id, username FROM \"user\" WHERE role = 'teacher' ORDER BY username")
        teachers_rows = cursor.fetchall()
        teachers = [dict(r) for r in teachers_rows]
    except Exception as e:
        print(f"Error loading classes/teachers: {e}")
        classes = []
        teachers = []
    
    # Get selected class and teacher from query parameters or form
    selected_class_id = request.args.get('class_id') or request.form.get('class_id')
    selected_teacher_id = request.args.get('teacher_id') or request.form.get('teacher_id')
    
    students = []
    periods_today = []
    current_period = None
    attendance_records = {}
    today = get_current_date().strftime('%Y-%m-%d')
    present_count = 0
    absent_count = 0
    
    if selected_class_id and selected_teacher_id:
        try:
            # Fetch students for the selected class
            cursor.execute("""
                SELECT id, name FROM student 
                WHERE class_id = %s 
                ORDER BY name
            """, (selected_class_id,))
            students_rows = cursor.fetchall()
            students = [dict(r) for r in students_rows]
            
            # Get current date and day of week
            day_of_week = get_current_datetime().weekday()  # Monday=0, Sunday=6
            day_of_week = (day_of_week + 1) % 7  # Convert to Sunday=0, Monday=1
            
            # Fetch periods for today with teacher names from attendance records
            cursor.execute("""
                SELECT DISTINCT p.id, p.day_of_week, p.period_num, p.start_time, p.end_time,
                       u.username as teacher_name
                FROM period p
                LEFT JOIN attendance a ON a.period = p.period_num 
                    AND a.date = %s 
                    AND a.class_id = %s
                LEFT JOIN "user" u ON u.id = a.teacher_id
                WHERE p.day_of_week = %s 
                ORDER BY p.period_num
            """, (today, selected_class_id, day_of_week))
            periods_rows = cursor.fetchall()
            # Convert time objects to strings for JSON serialization
            periods_today = []
            for r in periods_rows:
                period_dict = dict(r)
                period_dict['start_time'] = str(period_dict['start_time']) if period_dict.get('start_time') else None
                period_dict['end_time'] = str(period_dict['end_time']) if period_dict.get('end_time') else None
                period_dict['teacher_name'] = period_dict.get('teacher_name')
                periods_today.append(period_dict)
            
            # Determine current period based on time
            current_period = determine_current_period(periods_today)
            
            # Fetch attendance records for today
            cursor.execute("""
                SELECT student_id, period, status, remark, notes 
                FROM attendance 
                WHERE class_id = %s AND date = %s
                ORDER BY student_id, period
            """, (selected_class_id, today))
            att_rows = cursor.fetchall()
            
            # Build attendance records dictionary
            for row in att_rows:
                key = f"{row['student_id']}_{row['period']}"
                attendance_records[key] = {
                    'status': row['status'],
                    'remark': row['remark'],
                    'notes': row['notes']
                }
            
            # Count present and absent
            for student in students:
                student_present = False
                for period in periods_today:
                    key = f"{student['id']}_{period['period_num']}"
                    if key in attendance_records:
                        if attendance_records[key]['status'] == 'present':
                            student_present = True
                            break
                
                if student_present:
                    present_count += 1
                else:
                    absent_count += 1
        
        except Exception as e:
            print(f"Error loading attendance data: {e}")
            import traceback
            traceback.print_exc()
    
    return render_template('public_attendance.html',
                         classes=classes,
                         teachers=teachers,
                         selected_class_id=selected_class_id,
                         selected_teacher_id=selected_teacher_id,
                         students=students,
                         periods_today=periods_today,
                         current_period=current_period,
                         attendance_records=attendance_records,
                         today=today,
                         present_count=present_count,
                         absent_count=absent_count)

@app.route('/attendance/save', methods=['POST'])
def save_public_attendance():
    """Save attendance records from public attendance page"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        today = get_current_date().strftime('%Y-%m-%d')
        
        # Get form data
        class_id = request.form.get('class_id')
        teacher_id = request.form.get('teacher_id')
        
        if not class_id or not teacher_id:
            return {'success': False, 'message': 'Class and teacher required'}, 400
        
        # Collect all form data
        for key in request.form.keys():
            if key.startswith('attendance_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    student_id = parts[1]
                    period = parts[2]
                    status_value = request.form.get(key)
                    remark = request.form.get(f'remark_{student_id}_{period}', '').strip()
                    notes = request.form.get(f'notes_{student_id}_{period}', '').strip()
                    
                    # Determine status: 'on' means present, else absent
                    attendance_status = 'present' if status_value == 'on' else 'absent'
                    
                    # Clear remark if status is present
                    if attendance_status == 'present':
                        remark = ''
                    
                    try:
                        # Check if record exists
                        cursor.execute("""
                            SELECT id FROM attendance 
                            WHERE student_id = %s AND date = %s AND period = %s AND class_id = %s
                        """, (student_id, today, period, class_id))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing
                            cursor.execute("""
                                UPDATE attendance 
                                SET status = %s, teacher_id = %s, remark = %s, notes = %s
                                WHERE id = %s
                            """, (attendance_status, teacher_id, remark if remark else None, 
                                  notes if notes else None, existing['id']))
                        else:
                            # Insert new
                            cursor.execute("""
                                INSERT INTO attendance (student_id, date, period, status, teacher_id, class_id, remark, notes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (student_id, today, period, attendance_status, teacher_id, class_id,
                                  remark if remark else None, notes if notes else None))
                    except Exception as e:
                        print(f"Error saving attendance for student {student_id}, period {period}: {e}")
                        continue
        
        conn.commit()
        flash('Attendance saved successfully', 'success')
        return redirect(url_for('public_attendance', class_id=class_id, teacher_id=teacher_id))
    
    except Exception as e:
        print(f"Error saving attendance: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error saving attendance: {str(e)}', 'danger')
        return redirect(url_for('public_attendance'))

@app.route('/attendance/save-remark', methods=['POST'])
def save_remark():
    """Save remark for absent student (AJAX endpoint)"""
    try:
        student_id = request.json.get('student_id')
        period = request.json.get('period')
        remark = request.json.get('remark', '').strip()
        class_id = request.json.get('class_id')
        teacher_id = request.json.get('teacher_id')
        
        if not all([student_id, period, class_id, teacher_id]):
            return {'success': False, 'message': 'Missing required fields'}, 400
        
        # Validate remark value
        if remark and remark not in ['excused', 'still absent']:
            return {'success': False, 'message': 'Invalid remark value'}, 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        today = get_current_date().strftime('%Y-%m-%d')
        
        # Update remark in attendance record
        cursor.execute("""
            UPDATE attendance 
            SET remark = %s
            WHERE student_id = %s AND date = %s AND period = %s AND class_id = %s
        """, (remark if remark else None, student_id, today, period, class_id))
        
        conn.commit()
        
        return {'success': True, 'message': 'Remark saved successfully'}, 200
    
    except Exception as e:
        print(f"Error saving remark: {e}")
        return {'success': False, 'message': str(e)}, 500

@app.route('/attendance/save-notes', methods=['POST'])
def save_notes():
    """Save notes for student attendance (AJAX endpoint)"""
    try:
        student_id = request.json.get('student_id')
        period = request.json.get('period')
        notes = request.json.get('notes', '').strip()
        class_id = request.json.get('class_id')
        teacher_id = request.json.get('teacher_id')
        
        if not all([student_id, period, class_id, teacher_id]):
            return {'success': False, 'message': 'Missing required fields'}, 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        today = get_current_date().strftime('%Y-%m-%d')
        
        # Update notes in attendance record
        cursor.execute("""
            UPDATE attendance 
            SET notes = %s
            WHERE student_id = %s AND date = %s AND period = %s AND class_id = %s
        """, (notes if notes else None, student_id, today, period, class_id))
        
        conn.commit()
        
        return {'success': True, 'message': 'Notes saved successfully'}, 200
    
    except Exception as e:
        print(f"Error saving notes: {e}")
        return {'success': False, 'message': str(e)}, 500

@app.route('/attendance/save-attendance-status', methods=['POST'])
def save_attendance_status():
    """Save individual attendance status (AJAX endpoint)"""
    try:
        student_id = request.json.get('student_id')
        period = request.json.get('period')
        status = request.json.get('status')
        class_id = request.json.get('class_id')
        teacher_id = request.json.get('teacher_id')
        
        if not all([student_id, period, status, class_id, teacher_id]):
            return {'success': False, 'message': 'Missing required fields'}, 400
        
        if status not in ['present', 'absent']:
            return {'success': False, 'message': 'Invalid status value'}, 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        today = get_current_date().strftime('%Y-%m-%d')
        
        # Check if record exists
        cursor.execute("""
            SELECT id FROM attendance 
            WHERE student_id = %s AND date = %s AND period = %s AND class_id = %s
        """, (student_id, today, period, class_id))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute("""
                UPDATE attendance 
                SET status = %s, teacher_id = %s
                WHERE id = %s
            """, (status, teacher_id, existing['id']))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO attendance (student_id, date, period, status, teacher_id, class_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, today, period, status, teacher_id, class_id))
        
        conn.commit()
        
        return {'success': True, 'message': 'Attendance saved successfully'}, 200
    
    except Exception as e:
        print(f"Error saving attendance: {e}")
        return {'success': False, 'message': str(e)}, 500

@app.route('/public-daily-attendance', methods=['GET'])
def public_daily_attendance():
    """Public page to view overall daily attendance per student"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all classes
    try:
        cursor.execute("SELECT id, name FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [dict(r) for r in classes_rows]
    except Exception as e:
        print(f"Error loading classes: {e}")
        classes = []
    
    # Get selected class and date from query parameters
    selected_class_id = request.args.get('class_id')
    selected_date = request.args.get('date', get_current_date().strftime('%Y-%m-%d'))
    
    students = []
    all_periods = []
    attendance_records = {}
    daily_attendance_records = {}
    
    if selected_class_id and selected_date:
        try:
            # Fetch students for the selected class
            cursor.execute("""
                SELECT id, name FROM student 
                WHERE class_id = %s 
                ORDER BY name
            """, (selected_class_id,))
            students_rows = cursor.fetchall()
            students = [dict(r) for r in students_rows]
            
            # Get all periods (all days)
            cursor.execute("""
                SELECT DISTINCT period_num 
                FROM period 
                ORDER BY period_num
            """)
            periods_rows = cursor.fetchall()
            all_periods = [{'period_num': r['period_num']} for r in periods_rows]
            
            # Fetch attendance records for the selected date
            cursor.execute("""
                SELECT student_id, period, status
                FROM attendance 
                WHERE class_id = %s AND date = %s
                ORDER BY student_id, period
            """, (selected_class_id, selected_date))
            att_rows = cursor.fetchall()
            
            # Build attendance records dictionary
            for row in att_rows:
                key = f"{row['student_id']}_{row['period']}"
                attendance_records[key] = {
                    'status': row['status']
                }
            
            # Fetch daily attendance records
            cursor.execute("""
                SELECT student_id, overall_status, notes
                FROM daily_attendance 
                WHERE date = %s
            """, (selected_date,))
            daily_att_rows = cursor.fetchall()
            
            for row in daily_att_rows:
                daily_attendance_records[str(row['student_id'])] = {
                    'overall_status': row['overall_status'],
                    'notes': row['notes']
                }
        
        except Exception as e:
            print(f"Error loading daily attendance data: {e}")
            import traceback
            traceback.print_exc()
    
    return render_template('public_daily_attendance.html',
                         classes=classes,
                         selected_class_id=selected_class_id,
                         selected_date=selected_date,
                         students=students,
                         all_periods=all_periods,
                         attendance_records=attendance_records,
                         daily_attendance_records=daily_attendance_records)

@app.route('/public-daily-attendance/save', methods=['POST'])
def save_public_daily_attendance():
    """Save daily attendance records"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get form data
        class_id = request.form.get('class_id')
        date = request.form.get('date')
        
        if not class_id or not date:
            flash('معلومات غير كاملة', 'danger')
            return redirect(url_for('public_daily_attendance'))
        
        # Get all students for the class
        cursor.execute("""
            SELECT id FROM student WHERE class_id = %s
        """, (class_id,))
        students = cursor.fetchall()
        
        # Process each student's overall status and notes
        for student in students:
            student_id = student['id']
            overall_status_key = f'overall_status_{student_id}'
            notes_key = f'notes_{student_id}'
            
            overall_status_value = request.form.get(overall_status_key, '')
            notes = request.form.get(notes_key, '').strip()
            
            # Determine final overall status
            if overall_status_value == 'present':
                final_status = 'present'
            elif overall_status_value == 'excused':
                final_status = 'present'
            elif overall_status_value == 'still_absent':
                final_status = 'absent'
            else:
                # If no value, check actual attendance
                cursor.execute("""
                    SELECT COUNT(*) as absent_count
                    FROM attendance
                    WHERE student_id = %s AND date = %s AND class_id = %s AND status = 'absent'
                """, (student_id, date, class_id))
                result = cursor.fetchone()
                if result and result['absent_count'] > 0:
                    final_status = 'absent'
                else:
                    final_status = 'present'
            
            # Check if record exists
            cursor.execute("""
                SELECT student_id FROM daily_attendance 
                WHERE student_id = %s AND date = %s
            """, (student_id, date))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE daily_attendance 
                    SET overall_status = %s, notes = %s
                    WHERE student_id = %s AND date = %s
                """, (final_status, notes if notes else None, student_id, date))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO daily_attendance (student_id, date, overall_status, notes)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, date, final_status, notes if notes else None))
        
        conn.commit()
        flash('تم حفظ الحضور اليومي بنجاح', 'success')
        return redirect(url_for('public_daily_attendance', class_id=class_id, date=date))
    
    except Exception as e:
        print(f"Error saving daily attendance: {e}")
        import traceback
        traceback.print_exc()
        flash(f'حدث خطأ أثناء حفظ الحضور: {str(e)}', 'danger')
        return redirect(url_for('public_daily_attendance'))

@app.route('/export-daily-attendance-excel', methods=['POST'])
def export_daily_attendance_excel():
    """Export daily attendance to Excel for selected classes"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get form data
        class_ids = request.form.getlist('class_ids')
        date = request.form.get('date', get_current_date().strftime('%Y-%m-%d'))
        
        if not class_ids:
            flash('يرجى اختيار صف واحد على الأقل', 'danger')
            return redirect(url_for('public_daily_attendance'))
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "الحضور اليومي"
        
        # Styles
        title_font = Font(name='Arial', size=16, bold=True)
        header_font = Font(name='Arial', size=12, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal='center', vertical='center')
        right_alignment = Alignment(horizontal='right', vertical='center')
        
        current_row = 1
        
        # Get all periods
        cursor.execute("""
            SELECT DISTINCT period_num 
            FROM period 
            ORDER BY period_num
        """)
        all_periods = [r['period_num'] for r in cursor.fetchall()]
        
        for class_id in class_ids:
            # Get class info
            cursor.execute("SELECT name FROM school_class WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()
            class_name = class_info['name'] if class_info else f"Class {class_id}"
            
            # Title
            ws.merge_cells(f'A{current_row}:E{current_row}')
            title_cell = ws[f'A{current_row}']
            title_cell.value = "تقرير الحضور اليومي"
            title_cell.font = title_font
            title_cell.alignment = center_alignment
            current_row += 1
            
            # Class and Date
            ws.merge_cells(f'A{current_row}:E{current_row}')
            class_cell = ws[f'A{current_row}']
            class_cell.value = f"الصف: {class_name} | التاريخ: {date}"
            class_cell.font = Font(name='Arial', size=12, bold=True)
            class_cell.alignment = center_alignment
            current_row += 1
            current_row += 1  # Empty row
            
            # Headers
            header_row = current_row
            ws[f'A{header_row}'] = "اسم الطالب"
            col_index = 2  # B column
            for period_num in all_periods:
                col_letter = chr(64 + col_index)
                ws[f'{col_letter}{header_row}'] = f"الحصة {period_num}"
                col_index += 1
            
            overall_col = chr(64 + col_index)
            ws[f'{overall_col}{header_row}'] = "الحالة العامة"
            col_index += 1
            notes_col = chr(64 + col_index)
            ws[f'{notes_col}{header_row}'] = "الملاحظات"
            
            # Apply header styling
            for col in range(1, col_index + 1):
                cell = ws.cell(row=header_row, column=col)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            current_row += 1
            data_start_row = current_row
            
            # Get students
            cursor.execute("""
                SELECT id, name FROM student 
                WHERE class_id = %s 
                ORDER BY name
            """, (class_id,))
            students = cursor.fetchall()
            
            # Statistics counters
            period_present_count = {p: 0 for p in all_periods}
            period_absent_count = {p: 0 for p in all_periods}
            overall_present_count = 0
            overall_absent_count = 0
            excused_count = 0
            
            for student in students:
                student_id = student['id']
                student_name = student['name']
                
                # Student name
                ws[f'A{current_row}'] = student_name
                ws[f'A{current_row}'].alignment = right_alignment
                
                # Get attendance for each period
                cursor.execute("""
                    SELECT period, status
                    FROM attendance 
                    WHERE student_id = %s AND date = %s AND class_id = %s
                """, (student_id, date, class_id))
                attendance_records = {r['period']: r['status'] for r in cursor.fetchall()}
                
                col_index = 2
                for period_num in all_periods:
                    col_letter = chr(64 + col_index)
                    status = attendance_records.get(period_num, '')
                    if status == 'present':
                        ws[f'{col_letter}{current_row}'] = "✓"
                        ws[f'{col_letter}{current_row}'].font = Font(color="00FF00", bold=True)
                        period_present_count[period_num] += 1
                    elif status == 'absent':
                        ws[f'{col_letter}{current_row}'] = "✗"
                        ws[f'{col_letter}{current_row}'].font = Font(color="FF0000", bold=True)
                        period_absent_count[period_num] += 1
                    else:
                        ws[f'{col_letter}{current_row}'] = "-"
                    ws[f'{col_letter}{current_row}'].alignment = center_alignment
                    col_index += 1
                
                # Get daily attendance (overall status)
                cursor.execute("""
                    SELECT overall_status, notes
                    FROM daily_attendance 
                    WHERE student_id = %s AND date = %s
                """, (student_id, date))
                daily_att = cursor.fetchone()
                
                # Overall status with remark
                if daily_att:
                    overall_status = daily_att['overall_status']
                    notes = daily_att['notes'] or ''
                    
                    if overall_status == 'present':
                        ws[f'{overall_col}{current_row}'] = "حاضر"
                        ws[f'{overall_col}{current_row}'].font = Font(color="008000", bold=True)
                        overall_present_count += 1
                        # Check if it was excused
                        if any(attendance_records.get(p) == 'absent' for p in all_periods):
                            excused_count += 1
                    else:
                        ws[f'{overall_col}{current_row}'] = "غائب"
                        ws[f'{overall_col}{current_row}'].font = Font(color="FF0000", bold=True)
                        overall_absent_count += 1
                    
                    ws[f'{notes_col}{current_row}'] = notes
                else:
                    # Determine from attendance records
                    has_absent = any(attendance_records.get(p) == 'absent' for p in all_periods)
                    if has_absent:
                        ws[f'{overall_col}{current_row}'] = "غائب"
                        ws[f'{overall_col}{current_row}'].font = Font(color="FF0000", bold=True)
                        overall_absent_count += 1
                    else:
                        ws[f'{overall_col}{current_row}'] = "حاضر"
                        ws[f'{overall_col}{current_row}'].font = Font(color="008000", bold=True)
                        overall_present_count += 1
                
                ws[f'{overall_col}{current_row}'].alignment = center_alignment
                ws[f'{notes_col}{current_row}'].alignment = right_alignment
                
                current_row += 1
            
            # Footer - Statistics
            current_row += 1
            footer_row = current_row
            ws[f'A{footer_row}'] = "الإحصائيات"
            ws[f'A{footer_row}'].font = Font(bold=True, size=12)
            current_row += 1
            
            # Period statistics
            ws[f'A{current_row}'] = "إحصائيات الحصص:"
            ws[f'A{current_row}'].font = Font(bold=True)
            current_row += 1
            
            col_index = 2
            for period_num in all_periods:
                col_letter = chr(64 + col_index)
                ws[f'{col_letter}{current_row}'] = f"الحصة {period_num}: حاضر {period_present_count[period_num]} | غائب {period_absent_count[period_num]}"
                col_index += 1
            current_row += 1
            
            # Overall status summary
            ws[f'A{current_row}'] = "ملخص الحالة العامة:"
            ws[f'A{current_row}'].font = Font(bold=True)
            current_row += 1
            
            ws[f'A{current_row}'] = f"إجمالي الحضور: {overall_present_count}"
            ws[f'A{current_row}'].font = Font(color="008000", bold=True)
            current_row += 1
            
            ws[f'A{current_row}'] = f"إجمالي الغياب: {overall_absent_count}"
            ws[f'A{current_row}'].font = Font(color="FF0000", bold=True)
            current_row += 1
            
            ws[f'A{current_row}'] = f"عدد المعفيين: {excused_count}"
            ws[f'A{current_row}'].font = Font(color="0000FF", bold=True)
            current_row += 3  # Space before next class
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        for col in range(2, col_index + 1):
            ws.column_dimensions[chr(64 + col)].width = 12
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Generate filename
        filename = f"daily_attendance_{date}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        import traceback
        traceback.print_exc()
        flash(f'حدث خطأ أثناء التصدير: {str(e)}', 'danger')
        return redirect(url_for('public_daily_attendance'))

@app.route('/attendance-tabs', methods=['GET'])
def attendance_tabs():
    """Public page to record attendance with class tabs"""
    # Get optional class_id and teacher_id from query parameters (for maintaining selection after save)
    selected_class_id = request.args.get('class_id')
    selected_teacher_id = request.args.get('teacher_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all classes
    classes = []
    try:
        cursor.execute("SELECT * FROM school_class ORDER BY name")
        classes_rows = cursor.fetchall()
        classes = [RowObject(dict(r)) for r in classes_rows]
    except Exception as e:
        print(f"Error loading classes: {e}")
    
    # Get today's day of week and periods
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    day_of_week = datetime.now().weekday()  # Monday=0, Sunday=6
    day_of_week = (day_of_week + 1) % 7  # Convert to Sunday=0, Monday=1
    
    periods_today = []
    try:
        # First try to get periods for today
        cursor.execute("""
            SELECT * FROM period 
            WHERE day_of_week = %s 
            ORDER BY period_num
            LIMIT 10
        """, (day_of_week,))
        periods_rows = cursor.fetchall()
        
        # If no periods for today, get periods from Sunday (day 0) as fallback
        if not periods_rows:
            cursor.execute("""
                SELECT * FROM period 
                WHERE day_of_week = 0
                ORDER BY period_num
                LIMIT 10
            """)
            periods_rows = cursor.fetchall()
        
        periods_today = [RowObject(dict(r)) for r in periods_rows]
        print(f"Loaded {len(periods_today)} periods for day {day_of_week}")
    except Exception as e:
        print(f"Error loading periods: {e}")
        import traceback
        traceback.print_exc()
    
    # Get teachers (users with role 'staff' - teachers are stored with staff role)
    teachers = []
    try:
        cursor.execute("""
            SELECT id, username FROM "user" 
            WHERE role = 'teacher' 
            ORDER BY username
        """)
        teachers_rows = cursor.fetchall()
        # Convert rows to RowObject with username as display name
        for row in teachers_rows:
            row_dict = dict(row)
            # Ensure we have both id and username for display
            row_dict['name'] = row_dict.get('username', '')
            teachers.append(RowObject(row_dict))
    except Exception as e:
        print(f"Error loading teachers: {e}")
        import traceback
        traceback.print_exc()
    
    # Build data structure for each class (OPTIMIZED - don't load all attendance records)
    classes_data = {}
    for cls in classes:
        try:
            # Ensure we have a valid class ID
            class_id = cls.id if hasattr(cls, 'id') and cls.id else (cls._row.get('id') if hasattr(cls, '_row') else None)
            
            if not class_id:
                print(f"Warning: Class has no ID - {cls}")
                continue
            
            # Get students in this class - convert class_id to appropriate type
            cursor.execute("""
                SELECT * FROM student 
                WHERE class_id = %s 
                ORDER BY name
                LIMIT 200
            """, (str(class_id),))
            students_rows = cursor.fetchall()
            students = [RowObject(dict(r)) for r in students_rows]
            
            # Load attendance records for today to show saved status
            attendance_records = {}
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE class_id = %s AND date = %s
            """, (str(class_id), today))
            att_rows = cursor.fetchall()
            for att_row in att_rows:
                att = dict(att_row)
                key = f"{att['student_id']}_{att['period']}"
                attendance_records[key] = att
            
            classes_data[class_id] = {
                'class': cls,
                'students': students,
                'attendance': attendance_records
            }
            print(f"Loaded class {class_id} with {len(students)} students and {len(attendance_records)} attendance records")
        except Exception as e:
            print(f"Error loading data for class {cls._row.get('id') if hasattr(cls, '_row') else 'unknown'}: {e}")
            import traceback
            traceback.print_exc()
            class_id = cls.id if hasattr(cls, 'id') else (cls._row.get('id') if hasattr(cls, '_row') else None)
            if class_id:
                classes_data[class_id] = {
                    'class': cls,
                    'students': [],
                    'attendance': {}
                }
    
    return render_template('attendance_tabs.html', 
                         classes=classes,
                         classes_data=classes_data,
                         periods_today=periods_today,
                         teachers=teachers,
                         today=today,
                         current_period=determine_current_period(periods_today),
                         selected_class_id=selected_class_id,
                         selected_teacher_id=selected_teacher_id)

@app.route('/attendance-tabs/save', methods=['POST'])
def save_attendance_tabs():
    """Save attendance records from the tabs page"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get all form data
        class_id = request.form.get('class_id')
        teacher_id = request.form.get('teacher_id')
        
        if not class_id or not teacher_id:
            flash('الصف والمدرس مطلوبان', 'danger')
            return redirect(url_for('attendance_tabs'))
        
        # Collect notes data
        notes_data = {}
        for key in request.form.keys():
            if key.startswith('notes_'):
                parts = key.split('_')
                if len(parts) >= 2:
                    student_id = parts[1]
                    notes_data[student_id] = request.form.get(key, '').strip()
        
        # Process attendance records
        for key in request.form.keys():
            if key.startswith('attendance_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    student_id = parts[1]
                    period = parts[2]
                    status_value = request.form.get(key)
                    
                    # Determine attendance status: 'on' means present, else absent
                    attendance_status = 'present' if status_value == 'on' else 'absent'
                    
                    # Get notes for this student
                    notes = notes_data.get(student_id, '')
                    
                    try:
                        # Check if attendance record exists
                        cursor.execute("""
                            SELECT id FROM attendance 
                            WHERE student_id = %s AND date = %s AND period = %s AND class_id = %s
                        """, (student_id, today, period, class_id))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing record
                            cursor.execute("""
                                UPDATE attendance 
                                SET status = %s, teacher_id = %s, notes = %s
                                WHERE id = %s
                            """, (attendance_status, teacher_id, notes if notes else None, existing['id']))
                        else:
                            # Insert new record
                            cursor.execute("""
                                INSERT INTO attendance (student_id, date, period, status, teacher_id, class_id, notes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (student_id, today, period, attendance_status, teacher_id, class_id, notes if notes else None))
                    except Exception as e:
                        print(f"Error saving attendance for student {student_id}, period {period}: {e}")
                        continue
        
        conn.commit()
        flash('تم حفظ الغياب بنجاح', 'success')
        # Redirect back to attendance page with class and teacher selected
        return redirect(url_for('attendance_tabs', class_id=class_id, teacher_id=teacher_id))
    except Exception as e:
        print(f"Error saving attendance: {e}")
        import traceback
        traceback.print_exc()
        flash(f'خطأ في حفظ الغياب: {str(e)}', 'danger')
        return redirect(url_for('attendance_tabs'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)