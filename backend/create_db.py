import MySQLdb

# Create connection to MySQL server (without specifying database)
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='admin',
    port=3306
)

cursor = conn.cursor()

# Create the database if it doesn't exist
try:
    cursor.execute("CREATE DATABASE IF NOT EXISTS tunifreelance_db;")
    print("Database created successfully or already exists")
except Exception as e:
    print(f"Error creating database: {e}")

cursor.close()
conn.close()
