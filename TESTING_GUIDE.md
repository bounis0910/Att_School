# 🌐 URLs & Testing Guide

## 📍 Live URLs

Your Flask app is running on:
```
http://127.0.0.1:5000/
http://192.168.3.173:5000/
```

Replace with your server IP if deployed elsewhere.

---

## 🔗 Public URLs (No Login Required)

### 1. Home Page with Manage Students Button
```
http://127.0.0.1:5000/
http://192.168.3.173:5000/
```
✅ Shows "Manage Students" button
✅ Click to access management page

### 2. Manage Students Page
```
http://127.0.0.1:5000/manage-students
http://192.168.3.173:5000/manage-students
```
✅ View all students
✅ Select class to filter
✅ Update phone numbers
✅ Export to Excel

### 3. Update Phone (Form Action)
```
POST http://127.0.0.1:5000/manage-students/<student_id>/update-phone

Form Data:
  phone1: <phone number>
  phone2: <phone number>
```
✅ Updates student record
✅ Redirects to manage_students

### 4. Export to Excel
```
http://127.0.0.1:5000/manage-students/export-excel?class_id=<class_id>

Example:
http://127.0.0.1:5000/manage-students/export-excel?class_id=5
```
✅ Downloads Excel file
✅ Named: ClassName_students_YYYY-MM-DD.xlsx

---

## 🧪 Testing Steps

### Test 1: View Home Page
```
1. Open browser
2. Go to: http://127.0.0.1:5000/
3. Verify: "Manage Students" button visible
4. Verify: School name displays correctly
5. ✅ PASS if button visible and clickable
```

### Test 2: Access Manage Students (No Login)
```
1. Click "Manage Students" button OR
2. Go to: http://127.0.0.1:5000/manage-students
3. Verify: No login prompt appears
4. Verify: Students display in table
5. ✅ PASS if students visible without login
```

### Test 3: Filter by Class
```
1. Go to manage-students page
2. Click class dropdown
3. Select a class (e.g., "12-A")
4. Verify: Students filtered to that class only
5. Verify: Export button appears
6. ✅ PASS if filtering works and export button appears
```

### Test 4: Update Phone Number
```
1. In manage-students page
2. Click [Edit] button on any student
3. Verify: Modal dialog opens
4. Verify: Student name displays
5. Verify: Phone fields pre-filled with current values
6. Update: Phone 1 value (e.g., "333444" → "999888")
7. Update: Phone 2 value (optional)
8. Click: [Save Changes]
9. Verify: Modal closes
10. Verify: Success message shows
11. Verify: Table updates with new values
12. ✅ PASS if update successful and displayed
```

### Test 5: Verify Database Update
```
1. After updating phone number
2. Refresh page (F5)
3. Verify: Updated phone number still displayed
4. ✅ PASS if value persisted to database
```

### Test 6: Export to Excel
```
1. Go to manage-students page
2. Select a class (e.g., "12-A")
3. Click [Export to Excel] button
4. Verify: File downloads (check downloads folder)
5. Verify: Filename format: "12-A_students_YYYY-MM-DD.xlsx"
6. Open Excel file
7. Verify: Header row has blue background
8. Verify: White text in header
9. Verify: All columns: ID, Name, National ID, Phone1, Phone2, Class
10. Verify: All students from selected class included
11. Verify: Phone numbers match what's displayed on page
12. ✅ PASS if Excel file correct and complete
```

### Test 7: Test with Different Classes
```
1. Go to manage-students
2. Select different classes one by one
3. Verify: Student list changes with each selection
4. Verify: Export button becomes available
5. Verify: Export downloads correct class data
6. ✅ PASS if all classes filter correctly
```

### Test 8: Test Error Handling
```
1. Try to update phone without selecting a class
2. Verify: Appropriate error message shows
3. Try invalid class ID in URL
4. Verify: Graceful error handling
5. ✅ PASS if errors handled gracefully
```

---

## 🌍 Accessing from Other Computers

If your app is on a different machine:

```
From same network:
http://<your-server-ip>:5000/

Example:
http://192.168.3.173:5000/manage-students

From internet (if exposed):
http://<your-domain>:5000/

Make sure port 5000 is open/accessible
```

---

## 🔍 Live Testing Log

Flask server shows these requests when testing:

```
GET / HTTP/1.1" 200                    ← Home page loaded
GET /manage-students HTTP/1.1" 200     ← Students page loaded
POST /manage-students/1/update-phone HTTP/1.1" 302  ← Phone updated (redirect)
GET /manage-students/export-excel?class_id=5 HTTP/1.1" 200  ← Excel exported
```

---

## 📊 Test Checklist

```
[ ] Home page displays correctly
[ ] "Manage Students" button visible
[ ] Can access /manage-students without login
[ ] Students display in table
[ ] Class filter works
[ ] Edit button opens modal
[ ] Phone fields pre-fill
[ ] Can update phone numbers
[ ] Update saves to database (persists after refresh)
[ ] Success message displays
[ ] Export button appears when class selected
[ ] Excel file downloads
[ ] Excel filename correct
[ ] Excel content correct
[ ] Multiple classes filter correctly
[ ] Error messages display appropriately
[ ] No authentication required for any operation
[ ] Mobile view responsive
[ ] All CSS loads correctly
```

---

## 🚨 Troubleshooting

### Issue: 404 Not Found on /manage-students
```
✓ Solution: Ensure app.py has the new routes
✓ Restart Flask app after changes
✓ Check app.py line count (should be ~1500 lines)
```

### Issue: Template Not Found Error
```
✓ Solution: Verify manage_students.html exists
✓ Location: d:\Att_School\templates\manage_students.html
✓ Restart Flask app
```

### Issue: No Database Connection
```
✓ Solution: Check PostgreSQL is running
✓ Verify DATABASE_URL in environment
✓ Check database credentials
```

### Issue: Excel Export Downloads Empty File
```
✓ Solution: Verify students exist in database
✓ Check class_id parameter is correct
✓ Verify openpyxl library installed
```

### Issue: Phone Updates Not Saving
```
✓ Solution: Check database connection
✓ Verify student table has phone1, phone2 columns
✓ Check Flask error logs
```

---

## 📝 Flask Error Logs

Monitor Flask output for errors:

```bash
# Run Flask with verbose output
python app.py

# Look for lines like:
ERROR: ...        ← Database errors
WARNING: ...      ← Non-critical issues
Traceback: ...    ← Python exceptions
```

---

## 🔒 Security Verification

### Test: Public Access (No Login)
```
✓ Can access /manage-students without login
✓ No authentication popup appears
✓ No redirect to login page
✓ Anyone can update phone numbers
✓ Anyone can export data
```

This is intentional design!

---

## 📱 Mobile Testing

### Test on Mobile Device
```
1. Get your server IP (e.g., 192.168.3.173)
2. On mobile: http://192.168.3.173:5000/
3. Verify layout adapts
4. Verify buttons clickable
5. Verify table scrolls
6. Verify modal works on mobile
```

---

## 🎯 Quick Test URLs

Copy & paste these to test:

```
Home:
http://127.0.0.1:5000/

Manage Students:
http://127.0.0.1:5000/manage-students

Export Class 1:
http://127.0.0.1:5000/manage-students/export-excel?class_id=1

Export Class 5:
http://127.0.0.1:5000/manage-students/export-excel?class_id=5

Existing Endpoints (for comparison):
http://127.0.0.1:5000/admin/login
http://127.0.0.1:5000/staff/login
http://127.0.0.1:5000/teacher/login
```

---

## ✅ Success Indicators

### When Everything Works
```
✅ Home page loads in < 1 second
✅ Students page loads in < 1 second
✅ Class filter works instantly
✅ Phone update completes in < 2 seconds
✅ Excel downloads in 1-2 seconds
✅ No error messages appear
✅ No JavaScript console errors
✅ All buttons clickable
✅ All links work
✅ Modal opens/closes smoothly
```

---

## 🎉 You're All Set!

Start testing by visiting:
```
http://127.0.0.1:5000/
```

Click "Manage Students" and enjoy!

---

**Created:** January 18, 2026
**Last Updated:** January 18, 2026
**Status:** Ready for Testing ✅
