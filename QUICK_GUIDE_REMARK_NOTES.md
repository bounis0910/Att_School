# Quick Reference: Remark and Notes Features

## How to Use the New Remark and Notes Columns

### Accessing the Attendance Page
1. Go to: `http://localhost:5000/attendance`
2. No login required
3. Select your class from the dropdown
4. Select your teacher from the dropdown

### Recording Attendance

#### Step 1: Mark Attendance
- Check/uncheck students based on their attendance
- Checked = Present ✓
- Unchecked = Absent ✗
- Only current period checkboxes are enabled

#### Step 2: Add Remarks (For Absent Students Only)
- A "الملاحظة" (Remark) dropdown appears **only for students marked as Absent**
- Select one of two options:
  - **معفى** (Excused) - Student has valid excuse
  - **غائب فعلا** (Still Absent) - Student has no excuse

**Important**: When you select "معفى" (Excused):
- The **Absent count decreases by 1**
- The **Present count increases by 1**
- The database is updated **automatically** (no need to save)

#### Step 3: Add Additional Notes
- Use the "الملاحظات" (Notes) column to add extra information
- You can write any text you want (e.g., "Doctor's appointment", "Family emergency")
- Notes are optional and have no character limit

#### Step 4: Save All Data
- Click the "حفظ الحضور" (Save Attendance) button at the bottom
- A spinner will appear while saving
- Notes and remarks are saved to the database

### Column Descriptions

| Column | Arabic | Purpose | Notes |
|--------|--------|---------|-------|
| Student Name | اسم الطالب | Shows student name | Required |
| Periods | فترات | Attendance for each period | Checkboxes enabled for current period only |
| Overall Status | الحالة العامة | Current overall status | Red ✗ if absent, Green ✓ if present |
| **Remark** | **الملاحظة** | Why student is absent | Shows dropdown only for absent students |
| **Notes** | **الملاحظات** | Additional comments | Optional text field |

### Remarks Options Explained

#### معفى (Excused)
- Use when student has a valid reason for absence
- Example: Doctor's appointment, family emergency, school event
- **Effect**: Counts are updated (absent -1, present +1)

#### غائب فعلا (Still Absent)
- Use when student has no excuse
- This is a regular unexcused absence
- **Effect**: No change to counts (student already marked as absent)

### Real-Time Updates

The system updates counts **immediately** when:
- ✅ You change a remark to "معفى" (Excused)
- ✅ You uncheck a student's attendance

No need to wait for the Save button to see count changes.

### Tips & Best Practices

1. **Always use Arabic labels** - System displays in Arabic for consistency
2. **Check remarks for absent students only** - Remark dropdown won't appear for present students
3. **Save when done** - Click the Save button to persist all changes to database
4. **Use notes for context** - Notes help explain attendance decisions later
5. **Review before saving** - Double-check all entries before clicking Save

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Remark dropdown not showing | Check that student is marked as Absent (unchecked) |
| Can't edit certain periods | Only current period is editable; others are read-only |
| Changes not saving | Click the "حفظ الحضور" (Save) button |
| Notes disappeared | Ensure you clicked Save button before leaving page |
| Counts not updating | Wait a moment for AJAX call to complete |

### Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Space**: Check/uncheck attendance checkbox
- **Enter**: Select from remark dropdown or save form
- **Arrow Keys**: Navigate dropdown options

### Mobile & Tablet

- All features work on mobile devices
- Text inputs and dropdowns are touch-friendly
- Landscape mode provides wider view of all columns

### Data Storage

All attendance data is stored with:
- Student name
- Class and teacher
- Period
- Date
- Status (Present/Absent)
- Remark (معفى/غائب فعلا)
- Notes (free text)
- Timestamps (created, updated)

### Export Notes

The attendance records can be exported with:
- Full attendance status
- All remarks
- Complete notes
- Searchable by remark type
- Filterable by absent/excused students

---

**For questions or issues, contact system administrator.**
