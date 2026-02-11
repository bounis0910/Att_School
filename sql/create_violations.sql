-- Migration: create violation table
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
);
