from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "kestrel_ops.db"


def validate_database() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Copy the supplied database to {DB_PATH}")
    if DB_PATH.stat().st_size == 0:
        raise ValueError(f"Database is empty: {DB_PATH}")


def connect() -> sqlite3.Connection:
    validate_database()
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@st.cache_data(ttl=900, show_spinner=False)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with connect() as connection:
        return pd.read_sql_query(sql, connection, params=params)

