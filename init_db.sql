-- Initial database schema and indexes
-- Run automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes after tables are created by Flask-SQLAlchemy
-- These will be added during migration

-- Performance-tuning parameters
ALTER DATABASE att_school SET shared_buffers = '256MB';
ALTER DATABASE att_school SET effective_cache_size = '1GB';
ALTER DATABASE att_school SET maintenance_work_mem = '64MB';
ALTER DATABASE att_school SET checkpoint_completion_target = 0.9;
ALTER DATABASE att_school SET wal_buffers = '16MB';
ALTER DATABASE att_school SET default_statistics_target = 100;
ALTER DATABASE att_school SET random_page_cost = 1.1;
ALTER DATABASE att_school SET effective_io_concurrency = 200;

-- Log slow queries
ALTER DATABASE att_school SET log_min_duration_statement = 500;

COMMENT ON DATABASE att_school IS 'Attendance Management System Database';
