# PostgreSQL Migration Setup Guide

## Prerequisites

1. PostgreSQL 12+ installed locally or on a server
2. Python 3.8+

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set up PostgreSQL

### Option A: Local PostgreSQL (Linux/Mac)

```bash
# Install PostgreSQL
# macOS
brew install postgresql@15

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
brew services start postgresql   # macOS
sudo service postgresql start     # Linux

# Create database user (if not exists)
sudo -u postgres psql -c "CREATE USER att_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "ALTER USER att_user CREATEDB;"
```

### Option B: Docker PostgreSQL

```bash
docker run --name att-postgres \
  -e POSTGRES_USER=att_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=att_school \
  -p 5432:5432 \
  -d postgres:15
```

## Step 3: Configure Connection

Create a `.env` file with your PostgreSQL credentials:

```
DATABASE_URL=postgresql+asyncpg://att_user:your_password@localhost:5432/att_school
SECRET_KEY=your-secret-key-here
TIMEZONE=Asia/Qatar
```

## Step 4: Run Migration

```bash
# This will:
# 1. Create att_school database (if not exists)
# 2. Migrate data from SQLite to PostgreSQL
# 3. Create indexes on critical columns

python migrate_to_postgresql.py
```

### Migration Output Example:

```
PostgreSQL Migration Tool
==================================================
Created PostgreSQL database: att_school
Starting migration from SQLite to PostgreSQL...
Migrating table: user
  ✓ Migrated 15 rows
Migrating table: student
  ✓ Migrated 250 rows
Migrating table: attendance
  ✓ Migrated 5000 rows
...
Creating indexes...
  ✓ Created index: idx_attendance_period_class_teacher
  ✓ Created index: idx_attendance_student_date_period
  ✓ Created index: idx_attendance_date_class
  ✓ Created index: idx_student_class

==================================================
Migration completed successfully!
```

## Step 5: Verify Database

```bash
# Connect to PostgreSQL
psql -U att_user -d att_school -h localhost

# Check tables
\dt

# Check indexes
\di

# Sample query
SELECT COUNT(*) FROM attendance;
```

## Step 6: Run Application

```bash
python app.py
```

## Step 7: Run Load Tests

```bash
python load_test.py
```

### Load Test Output Example:

```
============================================================
STARTING LOAD TESTS
============================================================
Testing: Query attendance by date and class... ✓ (45.23ms for 100 queries)
Testing: Query by period, class, teacher... ✓ (38.12ms for 100 queries)
Testing: Query student attendance... ✓ (52.34ms for 100 queries)
Testing: Update remark (simulated)... ✓ (22.45ms for 50 queries)
Testing: Count queries (staff dashboard)... ✓ (68.90ms for 150 queries)
Testing: Distinct periods query... ✓ (41.23ms for 100 queries)

============================================================
LOAD TEST RESULTS
============================================================

Query: attendance by date/class:
  Total calls: 100
  Avg time: 0.45ms
  Min time: 0.35ms
  Max time: 0.89ms
  Throughput: 2200 records/sec
...
```

## Database Indexes

The migration creates these indexes for optimal performance:

1. **idx_attendance_period_class_teacher** (Composite)

   - Columns: `period, class_id, teacher_id`
   - Use: Staff queries filtering by multiple criteria

2. **idx_attendance_student_date_period** (Composite)

   - Columns: `student_id, date, period`
   - Use: Individual student attendance lookups

3. **idx_attendance_date_class**

   - Columns: `date, class_id`
   - Use: Daily attendance reports

4. **idx_student_class**
   - Columns: `class_id`
   - Use: Student roster queries

## Troubleshooting

### Connection Refused

```
Error: could not connect to server: Connection refused
```

- Ensure PostgreSQL service is running
- Check DATABASE_URL in .env file
- Verify PostgreSQL port is 5432

### Authentication Failed

```
Error: FATAL: role "att_user" does not exist
```

- Create user: `sudo -u postgres createuser att_user`
- Set password: `ALTER USER att_user WITH PASSWORD 'password';`

### Database Already Exists

```
Error: database "att_school" already exists
```

- Drop existing: `DROP DATABASE att_school;`
- Or modify migration script to skip creation

### Permission Denied on SQLite

- Ensure you have read access to `app.db`
- Check file permissions: `ls -la app.db`

## Performance Comparison

### SQLite vs PostgreSQL

| Operation        | SQLite     | PostgreSQL |
| ---------------- | ---------- | ---------- |
| Single query     | 1-2ms      | 0.5-1ms    |
| 100 queries      | 150-200ms  | 45-60ms    |
| Concurrent (10x) | Locks DB   | 50-80ms    |
| Write operations | Sequential | Concurrent |
| Connections      | Limited    | Up to 100+ |

## Next Steps

1. Monitor query performance in production
2. Adjust indexes based on actual query patterns
3. Enable query logging for optimization: `echo_pool=True`
4. Consider connection pooling for high traffic

## Rollback to SQLite

If you need to revert:

```bash
# Stop the application
# Restore from backup or keep using local SQLite

# Update app configuration
# Set DATABASE_URL back to SQLite format
```

## Reference

- [SQLAlchemy AsyncIO Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg Docs](https://magicstack.github.io/asyncpg/current/)
- [PostgreSQL Index Docs](https://www.postgresql.org/docs/current/sql-createindex.html)
