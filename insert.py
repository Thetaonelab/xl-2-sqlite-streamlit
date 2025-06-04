import pandas as pd
import sqlite3

# Load Excel file (make sure to use openpyxl engine for .xlsx)
df = pd.read_excel('data/wellprod 06.04.25 mt.XLSX', engine='openpyxl')
# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('petro-wellprod-06042025.db')

# Insert data into a table (replace if it already exists)
df.to_sql('production', conn, if_exists='replace', index=False)

conn.close()
print("Excel data inserted into SQLite successfully.")
