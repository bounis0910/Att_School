# Local PostgreSQL Setup Guide

## Step 1: Install PostgreSQL on Linux

```bash
# Update package manager
sudo apt update

# Install PostgreSQL server and client
sudo apt install -y postgresql postgresql-contrib

# Verify installation
psql --version
```

## Step 2: Start PostgreSQL Service

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Enable PostgreSQL to start on boot
sudo systemctl enable postgresql

# Check service status
sudo systemctl status postgresql
```

## Step 3: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In the PostgreSQL shell, run:
CREATE USER att_user WITH PASSWORD 'your_secure_password';
ALTER ROLE att_user SET client_encoding TO 'utf8';
ALTER ROLE att_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE att_user SET default_transaction_deferrable TO on;
ALTER ROLE att_user SET default_transaction_read_committed TO off;
ALTER ROLE att_user SET timezone TO 'UTC';

CREATE DATABASE attendance_db OWNER att_user;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO att_user;

# Exit PostgreSQL shell
\q
```

## Step 4: Configure Environment

Create a `.env` file in your project root:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://att_user:your_secure_password@localhost:5432/attendance_db
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
TIMEZONE=Asia/Qatar
```

## Step 5: Test Connection

```bash
# Test connection as att_user
psql -U att_user -d attendance_db -h localhost
```

## Step 6: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 7: Initialize Database

```bash
# From your Flask app directory
flask --app app init-db
flask --app app add-attendance-columns
```

## Step 8: Create Indexes

The app will create indexes automatically on startup, but you can manually create them:

```bash
psql -U att_user -d attendance_db << EOF
CREATE INDEX idx_attendance_period ON attendance(period);
CREATE INDEX idx_attendance_class_id ON attendance(class_id);
CREATE INDEX idx_attendance_teacher_id ON attendance(teacher_id);
CREATE INDEX idx_attendance_student_id_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_date_class ON attendance(date, class_id);
\q
EOF
```

## Troubleshooting

### Permission Denied Error

```bash
# Fix PostgreSQL socket permissions
sudo chmod 775 /var/run/postgresql
sudo chmod 775 /var/run/postgresql/.s.PGSQL.5432
```

### Can't Connect to PostgreSQL

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Reset PostgreSQL Password

```bash
sudo -u postgres psql
ALTER USER att_user WITH PASSWORD 'new_password';
\q
```

### Drop and Recreate Database

```bash
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS attendance_db;
DROP USER IF EXISTS att_user;

CREATE USER att_user WITH PASSWORD 'your_secure_password';
ALTER ROLE att_user SET client_encoding TO 'utf8';
ALTER ROLE att_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE att_user SET default_transaction_deferrable TO on;

CREATE DATABASE attendance_db OWNER att_user;
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO att_user;
\q
EOF
```

## Backup and Restore

### Backup Database

```bash
pg_dump -U att_user -d attendance_db > attendance_backup.sql
```

### Restore Database

```bash
psql -U att_user -d attendance_db < attendance_backup.sql
```

## Performance Tuning

Edit `/etc/postgresql/*/main/postgresql.conf`:

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Recommended settings for a local development machine:

```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

Then restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## Next Steps

1. Update your Flask app to use PostgreSQL
2. Run migrations
3. Run load tests
4. Monitor performance with `pgAdmin` or `psql`
