-- Create daily_attendance table for overall daily attendance status
CREATE TABLE IF NOT EXISTS daily_attendance (
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    overall_status VARCHAR(20) NOT NULL DEFAULT 'present',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, date),
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    CHECK (overall_status IN ('present', 'absent'))
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_daily_attendance_date ON daily_attendance(date);
CREATE INDEX IF NOT EXISTS idx_daily_attendance_student ON daily_attendance(student_id);
