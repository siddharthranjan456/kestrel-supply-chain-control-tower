import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import cold_chain_deliveries, near_expiry, returns_data, service_orders
from src.service_metrics import aggregate_service

START_DATE, END_DATE = "2026-04-01", "2026-06-30"
st.set_page_config(page_title="Kestrel Control Tower", page_icon="📦", layout="wide")
st.title("Kestrel Provisions — Supply Chain Control Tower")
st.caption("FY2026–27 Q1 | 1 April–30 June 2026")

try:
    service = service_orders(START_DATE, END_DATE)
    cold = cold_chain_deliveries(START_DATE, END_DATE)
    expiry = near_expiry(END_DATE)
    returns = returns_data(START_DATE, END_DATE)
except Exception as exc:
    st.error(f"Unable to load operational data: {exc}")
    st.stop()

regions = ["All"] + sorted(service["region"].dropna().unique().tolist())
region = st.sidebar.selectbox("Regional view", regions)
quantity_basis = st.sidebar.radio("Fill-rate basis", ["Eaches", "Case Equivalent"])
if region != "All":
    service = service[service.region == region]
    cold = cold[cold.region == region]
    returns = returns[returns.region == region]

ordered = service["ordered_eaches"].sum() if quantity_basis == "Eaches" else service["ordered_cases"].sum()
delivered = service["delivered_eaches"].sum() if quantity_basis == "Eaches" else service["delivered_cases"].sum()
fill = delivered / ordered if ordered else 0
otif = service["otif"].mean() if len(service) else 0
excursion = cold["temperature_excursion_flag"].mean() if len(cold) else 0
leakage = returns["credit_note_value_inr"].sum()
expiry_value = expiry["estimated_trade_value_inr"].sum()

cols = st.columns(5)
cols[0].metric("Fill rate", f"{fill:.1%}")
cols[1].metric("OTIF", f"{otif:.1%}")
cols[2].metric("Chilled excursions", f"{excursion:.1%}")
cols[3].metric("Q1 credit-note leakage", f"₹{leakage/1e5:,.1f}L")
cols[4].metric("Near-expiry exposure", f"₹{expiry_value/1e5:,.1f}L")

left, right = st.columns(2)
by_region = aggregate_service(service, "region")
metric = "fill_rate_eaches" if quantity_basis == "Eaches" else "fill_rate_cases"
with left:
    st.subheader("Service by region")
    st.plotly_chart(px.bar(by_region, x="region", y=metric, color=metric, range_y=[0,1], labels={metric:"Fill rate"}), use_container_width=True)
with right:
    st.subheader("Credit-note leakage by category")
    leakage_category = returns.groupby("category", as_index=False)["credit_note_value_inr"].sum().sort_values("credit_note_value_inr", ascending=False)
    st.plotly_chart(px.bar(leakage_category, x="category", y="credit_note_value_inr", labels={"credit_note_value_inr":"Credit notes (₹)"}), use_container_width=True)

st.subheader("Immediate attention")
worst = aggregate_service(service, "outlet_name").nsmallest(10, metric)
st.dataframe(worst[["outlet_name",metric,"otif_rate","orders"]], use_container_width=True, hide_index=True)

