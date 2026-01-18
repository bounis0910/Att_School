# User Guide: Staff Students Management Page

## Page Access
- **URL:** `http://your-app/staff/students`
- **Accessible to:** Staff and Admin users
- **Entry point:** Click "Manage Students" button on Staff Dashboard

---

## Page Layout

### Header Section
```
┌──────────────────────────────────────┬──────────────────────┐
│ Students by Class                    │ [Back to Dashboard]  │
└──────────────────────────────────────┴──────────────────────┘
```

### Class Selection Card
```
┌─ Select Class ───────────────────────────────────┐
│  Choose Class: [Dropdown ▼]  [Export to Excel]   │
└──────────────────────────────────────────────────┘
```

### Students Table (Per Class)
```
┌─ Class: 12-A (25 student(s)) ─────────────────────────────────────────┐
│                                                                        │
│  #│ Student Name │ National ID │ Phone 1      │ Phone 2      │ Actions │
├──┼──────────────┼─────────────┼──────────────┼──────────────┼─────────┤
│ 1│ Ahmed Hassan │ 1234567890  │ 33334444     │ 55556666     │ [Edit]  │
│ 2│ Fatima Ali   │ 9876543210  │ 77778888     │ —            │ [Edit]  │
│ 3│ Mohammed Said│ 5555555555  │ 11112222     │ 33334444     │ [Edit]  │
│..│...          │...          │...           │...           │...      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Workflows

### Workflow 1: View Students by Class

1. **Initial Load**
   - Page loads with "All Students" option selected
   - All classes displayed with their students

2. **Select Class**
   - Click dropdown and choose a specific class
   - Table automatically filters to show only that class
   - "Export to Excel" button appears

3. **View Details**
   - See student name, national ID, and phone numbers
   - Quick scan of contact information

---

### Workflow 2: Update Phone Numbers

1. **Click Edit Button**
   ```
   Student Row: Ahmed Hassan | 1234567890 | 33334444 | 55556666 | [Edit] ←
   ```

2. **Modal Opens**
   ```
   ╔════════════════════════════════════╗
   ║ Update Phone Numbers               ║ [X]
   ╠════════════════════════════════════╣
   ║ Student: Ahmed Hassan              ║
   ║                                    ║
   ║ Phone 1 [________________]         ║
   ║ Primary phone number               ║
   ║                                    ║
   ║ Phone 2 [________________]         ║
   ║ Secondary phone number (optional)  ║
   ╠════════════════════════════════════╣
   ║ [Cancel]  [Save Changes]           ║
   ╚════════════════════════════════════╝
   ```

3. **Edit & Save**
   - Clear and enter new phone numbers
   - Click "Save Changes"
   - Modal closes automatically
   - Table updates with new numbers
   - Success message displayed

4. **Result**
   ```
   ✓ Flash message: "Phone numbers updated successfully"
   Student Row: Ahmed Hassan | 1234567890 | [NEW] | [NEW] | [Edit]
   ```

---

### Workflow 3: Export Students to Excel

1. **Select Class**
   - Use dropdown to select a class

2. **Export Button Appears**
   - Button labeled "Export to Excel" becomes visible
   - Click to download file

3. **Excel File Downloaded**
   - Filename: `12-A_students_2026-01-18.xlsx`
   - File contains:
     - Header row (blue background, white text)
     - All students from selected class
     - Columns: ID, Student Name, National ID, Phone 1, Phone 2, Class

4. **Excel Content Example**
   ```
   ┌────┬────────────────┬────────────────┬─────────┬─────────┬─────────┐
   │ ID │ Student Name   │ National ID    │ Phone 1 │ Phone 2 │ Class   │
   ├────┼────────────────┼────────────────┼─────────┼─────────┼─────────┤
   │ 1  │ Ahmed Hassan   │ 1234567890     │ 3334444 │ 5556666 │ 12-A    │
   │ 2  │ Fatima Ali     │ 9876543210     │ 7778888 │ —       │ 12-A    │
   │ 3  │ Mohammed Said  │ 5555555555     │ 1112222 │ 3334444 │ 12-A    │
   └────┴────────────────┴────────────────┴─────────┴─────────┴─────────┘
   ```

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Class Filter** | Dropdown to select specific class |
| **Student Count** | Shows number of students per class |
| **Phone Numbers** | Displays both phone1 and phone2 |
| **Edit Modal** | Clean interface for updating contact info |
| **Excel Export** | Professional formatted spreadsheet download |
| **Responsive Design** | Works on desktop, tablet, and mobile |
| **Navigation** | Easy back button to dashboard |

---

## Icons Used

| Icon | Meaning |
|------|---------|
| 👥 | People/Students |
| ⏳ | Funnel/Filter |
| 📁 | Collection/Class |
| ✏️ | Edit/Pencil |
| 📊 | Excel/Spreadsheet |
| ⬅️ | Back/Previous |
| ℹ️ | Information/Alert |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit form in modal |
| `Escape` | Close modal (cancel) |
| `Tab` | Move between phone fields |

---

## Error Handling

### Scenario: No students in class
```
ℹ️ No students found for the selected class.
```

### Scenario: No class selected
```
ℹ️ Select a class to view students.
```

### Scenario: Update fails
```
⚠️ Error updating phone numbers: [Error message]
```

### Scenario: Export fails
```
⚠️ Error exporting Excel: [Error message]
```

---

## Tips for Users

✅ **Best Practices:**
- Always verify phone numbers before exporting
- Update phone numbers in batches to save time
- Export Excel files after making updates for records
- Use descriptive phone numbers (include country code if international)

⚠️ **Things to Note:**
- Phone 1 is primary contact number
- Phone 2 is optional (can be left empty)
- Changes are saved immediately to database
- Excel export includes data at time of export
- Exported files are not automatically saved to server

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see "Manage Students" button | Verify you're logged in as Staff or Admin |
| Modal won't open | Try refreshing the page |
| Changes not saved | Ensure form submission completes (check browser console) |
| Export button disabled | Select a class first |
| Excel file corrupted | Re-export, or try different browser |

---

## System Requirements

- **Browser:** Modern browser (Chrome, Firefox, Safari, Edge)
- **JavaScript:** Must be enabled
- **Permissions:** Staff or Admin role
- **Database:** Student table with phone1 and phone2 columns

