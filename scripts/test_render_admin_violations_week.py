import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from datetime import date

with app.test_request_context('/'):
    rows = [
        {'violation_name': 'Late', 'class_name': 'Class A', 'cnt': 5},
        {'violation_name': 'Disruption', 'class_name': 'Class B', 'cnt': 2},
    ]
    classes = [{'id':1,'name':'Class A'},{'id':2,'name':'Class B'}]
    week = date.today().isocalendar()[1]
    year = date.today().isocalendar()[0]
    monday = date.today()
    sunday = date.today()
    sel_class = ''
    html = render_template = None
    try:
        from flask import render_template
        html = render_template('admin_violations_week.html', rows=rows, monday=monday, sunday=sunday, week=week, year=year, classes=classes, sel_class=sel_class)
        print('Rendered length:', len(html))
        print(html[:800])
    except Exception as e:
        import traceback
        traceback.print_exc()
