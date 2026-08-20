import time
import pandas as pd
import requests
import streamlit as st

BASE_URL = "http://localhost:8088"
API_KEY = "kp_live_7f3a9c21"


def _get(session, path, params=None, attempts=7):
    for attempt in range(attempts):
        response = session.get(f"{BASE_URL}{path}", params=params, headers={"X-API-Key": API_KEY}, timeout=20)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            time.sleep(float(response.headers.get("Retry-After", 1)))
            continue
        if response.status_code == 503:
            time.sleep(min(2 ** attempt, 8))
            continue
        response.raise_for_status()
    raise RuntimeError(f"Partner API failed after {attempts} attempts")


@st.cache_data(ttl=3600, show_spinner=False)
def freight_invoices(start_date: str, end_date: str) -> pd.DataFrame:
    rows, cursor = [], None
    with requests.Session() as session:
        while True:
            params = {"limit": 200, "from": start_date, "to": end_date}
            if cursor:
                params["cursor"] = cursor
            payload = _get(session, "/v1/freight_invoices", params=params)
            rows.extend(payload.get("data", []))
            cursor = payload.get("next_cursor")
            if not cursor:
                break
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["freight_cost_inr"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0) / 100
        frame["detention_charge_inr"] = pd.to_numeric(frame["detention_charge"], errors="coerce").fillna(0) / 100
    return frame

