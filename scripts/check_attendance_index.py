import sqlite3
import os

DB='app.db'
if not os.path.exists(DB):
    print('DB not found:', DB)
    raise SystemExit(1)
con=sqlite3.connect(DB)
cur=con.cursor()
print('PRAGMA index_list(attendance):')
cur.execute("PRAGMA index_list('attendance')")
indexes=cur.fetchall()
print(indexes)
found=False
for idx in indexes:
    # idx format: seq, name, unique, origin, partial
    name=idx[1]
    unique=idx[2]
    print('\nIndex:', name, 'unique=', unique)
    cur.execute(f"PRAGMA index_info('{name}')")
    info=cur.fetchall()
    print('columns:', info)
    cols=[c[2] for c in info]
    if unique and cols==['student_id','date','period']:
        found=True

print('\nUnique constraint for (student_id, date, period) present?:', found)
con.close()
