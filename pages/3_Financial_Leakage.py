import plotly.express as px
import streamlit as st
from src.analytics import delivered_cases_by_warehouse, returns_data
from src.freight_api import freight_invoices

START_DATE, END_DATE = "2026-04-01", "2026-06-30"
st.set_page_config(page_title="Financial Leakage | Kestrel",layout="wide")
st.title("Financial Leakage")
returns=returns_data(START_DATE,END_DATE)
c1,c2,c3=st.columns(3)
c1.metric("Credit-note leakage",f"₹{returns.credit_note_value_inr.sum():,.0f}")
c2.metric("Returned eaches",f"{returns.returned_eaches.sum():,.0f}")
c3.metric("Cold-chain leakage",f"₹{returns.loc[returns.return_reason_code=='RT06_COLD_CHAIN_BREACH','credit_note_value_inr'].sum():,.0f}")

by_category=returns.groupby("category",as_index=False).credit_note_value_inr.sum().sort_values("credit_note_value_inr",ascending=False)
by_reason=returns.groupby("return_reason_code",as_index=False).credit_note_value_inr.sum().sort_values("credit_note_value_inr",ascending=False)
left,right=st.columns(2)
left.plotly_chart(px.bar(by_category,x="category",y="credit_note_value_inr"),use_container_width=True)
right.plotly_chart(px.bar(by_reason,x="return_reason_code",y="credit_note_value_inr"),use_container_width=True)

st.subheader("Actual billed freight from partner API")
try:
    invoices=freight_invoices(START_DATE,END_DATE)
    delivered=delivered_cases_by_warehouse(START_DATE,END_DATE)
    freight=invoices.groupby("warehouse_code",as_index=False).agg(freight_cost_inr=("freight_cost_inr","sum"),detention_charge_inr=("detention_charge_inr","sum"),invoice_count=("invoice_id","count"))
    freight=freight.merge(delivered,on="warehouse_code",how="left")
    freight["freight_per_case_inr"]=freight.freight_cost_inr/freight.delivered_cases
    st.metric("Q1 billed freight",f"₹{freight.freight_cost_inr.sum():,.0f}")
    st.plotly_chart(px.bar(freight,x="warehouse_name",y="freight_per_case_inr",hover_data=["invoice_count","freight_cost_inr"]),use_container_width=True)
    carrier=invoices.groupby("carrier_name",as_index=False).freight_cost_inr.sum().sort_values("freight_cost_inr",ascending=False)
    st.dataframe(carrier,hide_index=True,use_container_width=True)
except Exception as exc:
    st.warning(f"Freight API unavailable. Start partner_api/server.py. Detail: {exc}")

