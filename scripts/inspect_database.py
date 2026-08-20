import sqlite3
import pandas as pd

DB_PATH = "data/kestrel_ops.db"

with sqlite3.connect(DB_PATH) as connection:
    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """,
        connection,
    )["name"].tolist()

    for table in tables:
        print(f"\n{'=' * 60}")
        print(f"TABLE: {table}")
        print("=" * 60)

        schema = pd.read_sql_query(
            f"PRAGMA table_info('{table}')",
            connection,
        )
        print(schema[["name", "type"]].to_string(index=False))

        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]

        print(f"Rows: {count:,}")

        sample = pd.read_sql_query(
            f'SELECT * FROM "{table}" LIMIT 3',
            connection,
        )
        print(sample.to_string(index=False))