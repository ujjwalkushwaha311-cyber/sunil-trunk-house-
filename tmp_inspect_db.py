import sqlite3, os

DB = 'db.sqlite3'
print('DB exists:', os.path.exists(DB))
conn = sqlite3.connect(DB)
c = conn.cursor()
print('TABLES:')
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(row[0])
print('--- store_complaint create SQL ---')
for row in c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='store_complaint'"):
    print(row[0])
print('--- PRAGMA table_info(store_complaint) ---')
for row in c.execute("PRAGMA table_info('store_complaint')"):
    print(row)
print('--- migrations for store ---')
for row in c.execute("SELECT app, name, applied FROM django_migrations WHERE app='store'"):
    print(row)
conn.close()
