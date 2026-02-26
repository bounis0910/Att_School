import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from flask import render_template
from datetime import date

with app.test_request_context('/'):
    # Provide fake context data for template
    classes = [{'id': 1, 'name': 'Class A'}, {'id': 2, 'name': 'Class B'}]
    students = [{'id': 101, 'name': 'Ali', 'roll_number': 'A1'}, {'id': 102, 'name': 'Sara', 'roll_number': 'A2'}]
    violation_types = [{'id': 1, 'name': 'Late'}, {'id': 2, 'name': 'Disruption'}]
    sel_class = 1
    viol_by_student = {}
    viol_list_by_student = {101: [{'staff_name': 'MrX', 'violation_name': 'Late', 'lesson_name': 'Math'}]}
    default_date = date.today().isoformat()

    html = render_template('teacher_assign_violation.html', classes=classes, students=students, violation_types=violation_types, sel_class=sel_class, viol_by_student=viol_by_student, viol_list_by_student=viol_list_by_student, default_date=default_date)
    print('Rendered length:', len(html))
    # print small snippet
    print(html[:800])
