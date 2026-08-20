import plotly.express as px
import streamlit as st
from src.analytics import cold_chain_deliveries, near_expiry, returns_data

START_DATE, END_DATE = "2026-04-01", "2026-06-30"
st.set_page_config(page_title="Cold Chain | Kestrel", layout="wide")
st.title("Cold Chain and Expiry")
cold = cold_chain_deliveries(START_DATE, END_DATE)
expiry = near_expiry(END_DATE, 30)
returns = returns_data(START_DATE, END_DATE)
cold_returns = returns[returns.return_reason_code == "RT06_COLD_CHAIN_BREACH"]

c1,c2,c3,c4=st.columns(4)
c1.metric("Chilled deliveries",f"{len(cold):,}")
c2.metric("Excursions",f"{int(cold.temperature_excursion_flag.sum()):,}")
c3.metric("Excursions / 100",f"{100*cold.temperature_excursion_flag.mean():.2f}" if len(cold) else "—")
c4.metric("Cold-chain credit notes",f"₹{cold_returns.credit_note_value_inr.sum():,.0f}")

by_region=cold.groupby("region",as_index=False).agg(deliveries=("delivery_id","count"),excursions=("temperature_excursion_flag","sum"))
by_region["per_100"]=100*by_region.excursions/by_region.deliveries
st.plotly_chart(px.bar(by_region,x="region",y="per_100",color="per_100",labels={"per_100":"Excursions per 100 chilled deliveries"}),use_container_width=True)

st.subheader("Near-expiry inventory — latest snapshot on or before 30 June")
st.caption("Exposure is estimated trade value: available cases × case pack × current list price; it is not accounting cost.")
st.metric("30-day near-expiry exposure",f"₹{expiry.estimated_trade_value_inr.sum():,.0f}")
st.dataframe(expiry.head(30),hide_index=True,use_container_width=True)

