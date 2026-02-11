"""Apply all .sql files in the sql/ directory in alphabetical order."""
import os
import glob
import psycopg2


def parse_db_url(url):
    from urllib.parse import unquote
    url = url.replace('+asyncpg', '').replace('+psycopg2', '')
    url = url.replace('postgresql://', '')
    creds, host_db = url.rsplit('@', 1)
    user, password = creds.split(':', 1)
    user = unquote(user)
    password = unquote(password)
    if ':' in host_db:
        host, port_db = host_db.split(':')
        port, dbname = port_db.split('/', 1)
        port = int(port)
    else:
        host, dbname = host_db.split('/', 1)
        port = 5432
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': dbname
    }


def load_db_params():
    url = os.environ.get('DATABASE_URL')
    if not url:
        # fallback to same default used in app.py
        url = 'postgresql://postgres:Almana@Pg23@localhost:5432/alsisdb'
    return parse_db_url(url)


def main():
    dbp = load_db_params()
    conn = psycopg2.connect(**dbp)
    cur = conn.cursor()

    sql_dir = os.path.join(os.path.dirname(__file__), '..', 'sql')
    files = sorted(glob.glob(os.path.join(sql_dir, '*.sql')))
    if not files:
        print('No migration files found in', sql_dir)
        return

    for f in files:
        print('Applying', os.path.basename(f))
        with open(f, 'r') as fh:
            sql = fh.read()
            try:
                cur.execute(sql)
                conn.commit()
                print('Applied', f)
            except Exception as e:
                conn.rollback()
                print('Error applying', f, e)
                return

    cur.close()
    conn.close()
    print('Migrations applied successfully')

if __name__ == '__main__':
    main()
