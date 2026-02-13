-- Migration: Create violation types table (list of allowed violation names)
-- Run this with psql: psql "$DATABASE_URL" -f sql/create_violation_types_table.sql

CREATE TABLE IF NOT EXISTS violation_type (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_violation_type_status ON violation_type(status);
