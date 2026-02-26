import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, SimpleUser
from flask import session
import secrets

# Fake DB cursor/connection to avoid touching real DB
class FakeCursor:
    def __init__(self):
        self._last = None
    def execute(self, *args, **kwargs):
        self._last = args[0]
    def fetchone(self):
        return {'id': 999}
    def fetchall(self):
        return []
    @property
    def rowcount(self):
        return 1

class FakeConn:
    def cursor(self):
        return FakeCursor()
    def commit(self):
        pass
    def rollback(self):
        pass

# Monkeypatch get_db and login loader
app.get_db = lambda: FakeConn()
app.login_manager._user_callback = lambda uid: SimpleUser({'id': int(uid), 'username': 't', 'name': 'Teacher T', 'role': 'teacher', 'password': ''})

with app.test_client() as c:
    # debug: list registered routes
    print('Registered routes:')
    for r in sorted([str(x) for x in app.url_map.iter_rules()]):
        print(' ', r)
    with c.session_transaction() as sess:
        sess['_user_id'] = '1'
        token = secrets.token_urlsafe(16)
        sess['_csrf_token'] = token

    data = {
        'csrf_token': token,
        'class_id': '1',
        'student_id': '101',
        'violation_type_101': '1',
        'lesson_101': 'Math',
        'period_101': '2',
        'date': '2026-02-27'
    }

    try:
        resp = c.post('/teacher/assign_violation', data=data)
        print('POST Status code:', resp.status_code)
        loc = resp.headers.get('Location')
        print('Location header:', loc)
        # follow redirect if provided
        if loc:
            g = c.get(loc)
            print('GET after redirect status:', g.status_code)
            print('GET snippet:', g.data[:400])
        else:
            print('Response snippet:', resp.data[:400])
    except Exception as e:
        import traceback
        traceback.print_exc()
