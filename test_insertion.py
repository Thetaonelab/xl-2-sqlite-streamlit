import sqlite3
import pandas as pd


conn = sqlite3.connect('petro-mpvl.db')
cursor = conn.cursor()

# Show table structure
cursor.execute("PRAGMA table_info(production)")
print(cursor.fetchall())

# Show some rows
df_check = pd.read_sql("SELECT * FROM production LIMIT 5", conn)
print(df_check)

conn.close()
