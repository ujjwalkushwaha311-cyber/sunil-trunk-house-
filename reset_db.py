import os
import glob
import MySQLdb

# 1. Clean migrations
migrations_dir = r"c:\sunil trunk house\store\migrations"
files = glob.glob(os.path.join(migrations_dir, "*.py"))
for f in files:
    if not f.endswith("__init__.py"):
        os.remove(f)
        print(f"Deleted {f}")

# 2. Recreate MySQL database
try:
    db = MySQLdb.connect(host="localhost", user="root", passwd="anshikhasuraj@6386")
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS sunil_trunk_house")
    cursor.execute("CREATE DATABASE sunil_trunk_house")
    db.close()
    print("Database sunil_trunk_house dropped and created successfully.")
except Exception as e:
    print("MySQL Error:", e)
