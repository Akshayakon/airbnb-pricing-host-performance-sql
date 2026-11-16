"""Run every sql/*.sql file against airbnb.db, print results, save to results/*.csv."""
import sqlite3, pandas as pd
from pathlib import Path

Path("results").mkdir(exist_ok=True)
con = sqlite3.connect("airbnb.db")
for f in sorted(Path("sql").glob("*.sql")):
    df = pd.read_sql(f.read_text(), con)
    df.to_csv(Path("results") / f"{f.stem}.csv", index=False)
    print(f"\n=== {f.stem} ===\n{df.to_string(index=False)}")
