-- Migration: create violation_audit table
CREATE TABLE IF NOT EXISTS violation_audit (
    id SERIAL PRIMARY KEY,
    violation_id INTEGER,
    action VARCHAR(32),
    user_id INTEGER,
    username TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
