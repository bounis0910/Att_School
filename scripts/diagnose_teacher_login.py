import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

app.testing = True

with app.test_client() as c:
    try:
        r = c.get('/teacher/login')
        print('GET /teacher/login status:', r.status_code)
    except Exception as e:
        print('GET raised exception:')
        import traceback
        traceback.print_exc()

    try:
        r = c.post('/teacher/login', data={'email':'nonexistent@example.com','password':'x'})
        print('POST /teacher/login status:', r.status_code)
    except Exception as e:
        print('POST raised exception:')
        import traceback
        traceback.print_exc()
