import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")
df = pd.read_sql("SELECT input_tokens FROM spans WHERE name = 'llm'", conn)
print(df['input_tokens'].describe())
print(f"Std dev: {df['input_tokens'].std():.2f}")
print(f"Mean: {df['input_tokens'].mean():.2f}")
print(f"CV: {df['input_tokens'].std() / df['input_tokens'].mean():.2%}")