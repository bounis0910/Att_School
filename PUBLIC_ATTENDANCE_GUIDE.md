# Public Attendance Recording System

## Overview

A new public attendance recording page has been added to the system that allows quick and easy attendance recording without requiring login. The page provides an intuitive interface for selecting a class and teacher, then recording attendance for students with period-specific controls.

## Features

### 1. **No Login Required**
- Accessible via `/attendance` endpoint
- Anyone can record attendance without credentials
- Designed for quick access in school settings

### 2. **Class and Teacher Selection**
- Dropdown menus to select class and teacher
- Auto-submit on selection for seamless navigation
- Selected values persist when viewing attendance records

### 3. **Period-Based Attendance Recording**
- **Horizontal layout**: Periods shown as column headers
- **Vertical layout**: Students listed as rows
- **Current period highlighting**: Yellow background indicator
- **Period timing**: Shows start and end times for each period

### 4. **Smart Checkbox Control**
- Checkboxes enabled **only for the current period**
- Other periods show disabled checkboxes (visual reference)
- Checked = Present, Unchecked = Absent
- Pre-populated with existing attendance data

### 5. **Remark System for Absent Students**
- Remark dropdown appears **only for absent students in the current period**
- Two remark options:
  - **معفى (Excused)**: Student is excused from attendance
  - **غائب فعلا (Still Absent)**: Student is marked absent without excuse
- Remarks saved automatically via AJAX
- Changes reflected immediately in present/absent counts

### 6. **Real-Time Statistics**
- **Present Count**: Number of students marked present
- **Absent Count**: Number of students marked absent
- Counts updated automatically when:
  - Checkbox status changes
  - Remark is saved (excused = treat as present)

### 7. **Data Persistence**
- **Save Attendance**: Submit button saves all attendance records
- Database fields saved:
  - `student_id`: Student identifier
  - `class_id`: Class identifier
  - `period`: Period number
  - `teacher_id`: Teacher identifier
  - `date`: Date of attendance
  - `status`: 'present' or 'absent'
  - `remark`: Optional remark ('excused' or 'still absent')
  - `notes`: Additional notes

### 8. **Smart Remark Handling**
- **Automatic Clearing**: When changing status from absent to present, remark is cleared
- **Excused = Present**: Selecting "excused" counts the student as present
- **Page Reload Optional**: Remark saves without requiring form submission

## User Workflow

1. **Select Class**: Choose class from dropdown
2. **Select Teacher**: Choose teacher from dropdown  
3. **View Attendance Table**: 
   - Students listed vertically
   - Periods listed horizontally
   - Current period highlighted in yellow
4. **Record Attendance**:
   - Check/uncheck boxes for current period only
   - Disabled checkboxes for past/future periods
5. **Add Remarks** (if needed):
   - For absent students, select excused or still absent
   - Changes apply immediately
6. **Save**: Click "حفظ الحضور" (Save Attendance) button
7. **Confirmation**: Flash message indicates success

## Technical Details

### Routes

#### GET `/attendance`
- Display attendance recording interface
- Query parameters:
  - `class_id` (optional): Pre-select class
  - `teacher_id` (optional): Pre-select teacher

#### POST `/attendance/save`
- Save attendance records
- Form data:
  - `class_id`: Selected class
  - `teacher_id`: Selected teacher
  - `attendance_[student_id]_[period]`: Checkbox values
  - `remark_[student_id]_[period]`: Remark values

#### POST `/attendance/save-remark` (AJAX)
- Save individual remarks for absent students
- JSON payload:
  ```json
  {
    "student_id": 123,
    "period": 1,
    "remark": "excused",
    "class_id": 456,
    "teacher_id": 789
  }
  ```
- Returns: `{success: true/false, message: string}`

### Database Schema

**attendance** table:
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    period INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'absent',
    remark VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Current Period Detection

The system automatically determines the current period based on:
1. **Time Range**: Compares current time with `start_time` and `end_time` in the period table
2. **Fallback**: If no period matches by time, uses the first period of the day

### Styling

- **Color Scheme**:
  - Primary: #366092 (blue)
  - Success: #28a745 (green)
  - Current Period: #ffc107 (yellow)
  - Present: Green badge
  - Absent: Red badge

- **Responsive Design**: 
  - Works on desktop and mobile devices
  - Adjustable table width for different screen sizes

## How to Use

1. Navigate to `/attendance`
2. Select class and teacher from dropdowns
3. The attendance table loads automatically
4. Check/uncheck boxes for the current period
5. For absent students, optionally add remarks
6. Click "حفظ الحضور" (Save Attendance) to save all changes

## Notes

- Only the current period's checkboxes are enabled
- Remarks are only shown for absent students in the current period
- Selecting "excused" immediately updates the counts
- The page reloads after saving to reflect any server-side changes
- All timestamps are stored with timezone information
