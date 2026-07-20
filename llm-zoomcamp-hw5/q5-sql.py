import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")
df = pd.read_sql("SELECT name, start_time, end_time FROM spans WHERE name != 'rag'", conn)
df['duration_ms'] = (df['end_time'] - df['start_time']) / 1_000_000
print(df.groupby('name')['duration_ms'].sum())