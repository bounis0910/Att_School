# PostgreSQL Migration Checklist

## Pre-Migration
- [ ] Backup current SQLite database
  ```bash
  cp app.db app.db.backup
  ```
- [ ] Review requirements.txt
- [ ] Plan downtime (if any)

## Installation (Choose One)

### Option A: Automated Setup (Recommended)
- [ ] Run automated setup script
  ```bash
  chmod +x setup_postgresql.sh
  bash setup_postgresql.sh
  ```

### Option B: Manual Setup
- [ ] Install PostgreSQL: `sudo apt install -y postgresql postgresql-contrib`
- [ ] Start service: `sudo systemctl start postgresql`
- [ ] Create user: `sudo -u postgres psql` then run SQL commands
- [ ] Create .env file with DATABASE_URL
- [ ] Install Python dependencies: `pip install psycopg2-binary python-dotenv`
- [ ] Initialize database: `flask --app app init-db`

## Data Migration
- [ ] Verify PostgreSQL is running and accessible
- [ ] Backup SQLite data one more time
- [ ] Run migration script (if migrating existing data)
  ```bash
  python migrate_sqlite_to_postgres.py
  ```
- [ ] Verify data integrity
  ```bash
  psql -U att_user -d attendance_db -c "SELECT COUNT(*) FROM attendance;"
  ```

## Configuration
- [ ] Update .env file with correct DATABASE_URL
- [ ] Set TIMEZONE to Asia/Qatar
- [ ] Set FLASK_ENV to development or production
- [ ] Generate new SECRET_KEY

## Verification
- [ ] Test database connection
  ```bash
  psql -U att_user -d attendance_db -c "SELECT NOW();"
  ```
- [ ] Check tables exist
  ```bash
  psql -U att_user -d attendance_db -c "\dt"
  ```
- [ ] Verify indexes created
  ```bash
  psql -U att_user -d attendance_db -c "SELECT * FROM pg_indexes WHERE tablename='attendance';"
  ```

## Application Testing
- [ ] Start Flask app: `python app.py`
- [ ] Test admin login
- [ ] Test staff dashboard
- [ ] Test teacher attendance recording
- [ ] Test attendance export
- [ ] Test remark updates
- [ ] Test notes functionality

## Performance Testing
- [ ] Run load tests: `python load_test.py`
- [ ] Monitor query performance
- [ ] Check database size
- [ ] Verify indexes are being used
  ```bash
  psql -U att_user -d attendance_db -c "EXPLAIN ANALYZE SELECT * FROM attendance WHERE period = 10 AND class_id = 1;"
  ```

## Backup & Recovery
- [ ] Test backup procedure
  ```bash
  pg_dump -U att_user -d attendance_db > backup_test.sql
  ```
- [ ] Test restore procedure (in test database)
- [ ] Document backup schedule
- [ ] Set up automated backups (if needed)

## Documentation
- [ ] Update deployment documentation
- [ ] Document connection string format
- [ ] Document user credentials location
- [ ] Document maintenance procedures

## Production Deployment (If Applicable)
- [ ] Test in staging environment first
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window
- [ ] Notify users of planned maintenance
- [ ] Perform migration
- [ ] Verify all systems operational
- [ ] Monitor for 24-48 hours post-migration

## Post-Migration
- [ ] Monitor application performance
- [ ] Check error logs
- [ ] Verify all features working
- [ ] Archive old SQLite database (after verification period)
- [ ] Update documentation with new setup

## Quick Commands Reference

### Database Management
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Check status
sudo systemctl status postgresql

# Connect to database
psql -U att_user -d attendance_db

# View database size
SELECT pg_size_pretty(pg_database_size('attendance_db'));

# List tables
\dt

# Show indexes on attendance table
SELECT * FROM pg_indexes WHERE tablename='attendance';
```

### Backup & Restore
```bash
# Backup
pg_dump -U att_user -d attendance_db > backup.sql

# Restore
psql -U att_user -d attendance_db < backup.sql

# Backup with compression
pg_dump -U att_user -d attendance_db | gzip > backup.sql.gz
```

### Application
```bash
# Initialize database
flask --app app init-db

# Add columns
flask --app app add-attendance-columns

# Start app
python app.py

# Run load test
python load_test.py
```

### Troubleshooting
```bash
# Check if PostgreSQL is running
ps aux | grep postgres

# Check listening ports
sudo netstat -tlnp | grep 5432

# View recent logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Connect as postgres user
sudo -u postgres psql

# List all users
\du

# List all databases
\l
```

---

**Last Updated:** November 26, 2025
**Status:** Ready for Migration
