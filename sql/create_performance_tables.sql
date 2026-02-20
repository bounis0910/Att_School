-- Create performance levels table and performance assignments table
CREATE TABLE IF NOT EXISTS performance_level (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
);

CREATE INDEX IF NOT EXISTS idx_performance_student_week ON performance(student_id, week_number);
CREATE INDEX IF NOT EXISTS idx_performance_class_week ON performance(class_id, week_number);
