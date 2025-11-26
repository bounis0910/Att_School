# PostgreSQL Migration Guide

## Overview

This guide will help you migrate the Attendance System from SQLite to PostgreSQL with proper indexing for performance optimization.

## Prerequisites

- Linux system (Ubuntu/Debian)
- Python 3.8+
- sudo access

## Quick Start (Automated)

```bash
# Make setup script executable
chmod +x setup_postgresql.sh

# Run setup script
./setup_postgresql.sh
```

This will:
1. Install PostgreSQL
2. Create database user and database
3. Create `.env` file
4. Install Python dependencies
5. Initialize database
6. Test connection

## Manual Setup

### Step 1: Install PostgreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
```

### Step 2: Start PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

### Step 3: Create User and Database

```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# In the psql shell, run:
CREATE USER att_user WITH PASSWORD 'your_secure_password';
ALTER ROLE att_user SET client_encoding TO 'utf8';
ALTER ROLE att_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE att_user SET default_transaction_deferrable TO on;
ALTER ROLE att_user SET default_transaction_read_committed TO off;
ALTER ROLE att_user SET timezone TO 'UTC';

CREATE DATABASE attendance_db OWNER att_user;
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO att_user;

\q
```

### Step 4: Install Python Dependencies

```bash
pip install psycopg2-binary python-dotenv flask flask-login werkzeug pandas openpyxl pytz
```

### Step 5: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Example `.env`:
```env
DATABASE_URL=postgresql+psycopg2://att_user:your_secure_password@localhost:5432/attendance_db
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TIMEZONE=Asia/Qatar
```

### Step 6: Initialize Database

```bash
# Create tables and schema
flask --app app init-db

# Add attendance columns if needed
flask --app app add-attendance-columns
```

## Data Migration from SQLite to PostgreSQL

If you have existing SQLite data:

```bash
python migrate_sqlite_to_postgres.py --sqlite app.db --postgres "postgresql://att_user:password@localhost:5432/attendance_db"
```

## Database Indexes

The system automatically creates these indexes:

```sql
-- Single column indexes
CREATE INDEX idx_attendance_period ON attendance(period);
CREATE INDEX idx_attendance_class_id ON attendance(class_id);
CREATE INDEX idx_attendance_teacher_id ON attendance(teacher_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(date);

-- Composite indexes
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_date_class ON attendance(date, class_id);

-- Foreign key indexes
CREATE INDEX idx_student_class_id ON student(class_id);
CREATE INDEX idx_period_class_id ON period(class_id);
CREATE INDEX idx_teacher_subject_teacher ON teacher_subject(teacher_id);
```

These indexes optimize queries for:
- Staff dashboard (date + class queries)
- Remark updates (student + date queries)
- Period lookups
- Teacher records filtering

## Performance Testing

```bash
# Run load tests
python load_test.py

# This tests:
# - Date & class queries: 200 operations
# - Period/class/teacher queries: 200 operations
# - Student attendance queries: 100 operations
# - Dashboard count queries: 100 iterations
# - Distinct periods queries: 100 operations
```

## Common Commands

### Connect to Database

```bash
# As att_user
psql -U att_user -d attendance_db -h localhost

# As postgres user
sudo -u postgres psql
```

### View Database Size

```bash
psql -U att_user -d attendance_db -c "SELECT pg_size_pretty(pg_database_size('attendance_db'));"
```

### Backup Database

```bash
pg_dump -U att_user -d attendance_db > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
psql -U att_user -d attendance_db < backup_20251126.sql
```

### Reset Database

```bash
# Drop and recreate (WARNING: Deletes all data)
sudo -u postgres dropdb attendance_db
sudo -u postgres psql -c "DROP USER att_user;"

# Then run setup again
bash setup_postgresql.sh
```

## Troubleshooting

### Error: "Can't connect to PostgreSQL"

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if it listens on port 5432
sudo netstat -tlnp | grep 5432

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Error: "Password authentication failed"

```bash
# Reset user password
sudo -u postgres psql -c "ALTER USER att_user WITH PASSWORD 'newpassword';"

# Update .env with new password
```

### Error: "Column does not exist"

```bash
# Check table schema
psql -U att_user -d attendance_db -c "\d attendance"

# Add missing columns
flask --app app add-attendance-columns
```

### Error: "Port 5432 already in use"

```bash
# Find process using port 5432
sudo lsof -i :5432

# Kill the process if needed
sudo kill -9 <PID>

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## Performance Optimization

### Increase shared_buffers

Edit `/etc/postgresql/*/main/postgresql.conf`:

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Recommended for development:
```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

Then restart:
```bash
sudo systemctl restart postgresql
```

## Monitoring

### Check Active Connections

```bash
psql -U att_user -d attendance_db -c "SELECT * FROM pg_stat_activity;"
```

### Check Index Usage

```bash
psql -U att_user -d attendance_db -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename = 'attendance' 
ORDER BY indexname;
"
```

### Check Query Performance

```bash
psql -U att_user -d attendance_db -c "EXPLAIN ANALYZE SELECT * FROM attendance WHERE period = 10 AND class_id = 1;"
```

## Next Steps

1. **Start the Flask application:**
   ```bash
   python app.py
   ```

2. **Run load tests:**
   ```bash
   python load_test.py
   ```

3. **Access the dashboard:**
   - Admin: http://localhost:5000/admin/login
   - Staff: http://localhost:5000/staff/login
   - Teacher: http://localhost:5000/teacher/login

4. **Monitor performance:**
   ```bash
   python load_test.py
   ```

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/)
- [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
