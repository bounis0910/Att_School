import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, SimpleUser
import secrets

class FakeCursor:
    def __init__(self, rows=None):
        self._rows = rows or []
        self._last_sql = None
    def execute(self, sql, params=None):
        self._last_sql = sql
    def fetchall(self):
        return self._rows
    def fetchone(self):
        return None

class FakeConn:
    def __init__(self, rows=None):
        self._rows = rows
    def cursor(self):
        return FakeCursor(self._rows)
    def commit(self):
        pass
    def rollback(self):
        pass

# Prepare fake aggregated rows
fake_rows = [
    {'violation_name': 'Late', 'class_name': 'Class A', 'cnt': 7},
    {'violation_name': 'Disruption', 'class_name': 'Class B', 'cnt': 3},
]

# Monkeypatch get_db to return fake connection
import app as app_module
app_module.get_db = lambda: FakeConn(rows=fake_rows)
# Ensure login loader returns admin user
app.login_manager._user_callback = lambda uid: SimpleUser({'id': int(uid), 'username': 'admin', 'name': 'Admin', 'role': 'admin', 'password': ''})

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['_user_id'] = '1'
    # Call export route
    resp = c.get('/admin/violations_week/export?week=1&year=2026')
    print('Status code:', resp.status_code)
    print('Content-Type:', resp.headers.get('Content-Type'))
    print('Content-Length:', len(resp.data))
    # Save file locally for inspection
    out = 'out_violations_week.xlsx'
    with open(out, 'wb') as fh:
        fh.write(resp.data)
    print('Wrote', out)
