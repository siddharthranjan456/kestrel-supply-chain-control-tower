from pathlib import Path
import sqlite3

path=Path(__file__).resolve().parents[1]/"data"/"kestrel_ops.db"
if not path.exists() or path.stat().st_size==0: raise SystemExit(f"Missing or empty database: {path}")
with sqlite3.connect(path) as con:
    for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        count=con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        print(f"\nTABLE {table} | ROWS {count:,}")
        for _,name,kind,required,_,pk in con.execute(f'PRAGMA table_info("{table}")'):
            print(f"  {name:30} {kind:12} PK={pk} NOT_NULL={required}")

