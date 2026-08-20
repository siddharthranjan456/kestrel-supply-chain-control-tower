import plotly.express as px
import streamlit as st
from src.analytics import service_orders
from src.service_metrics import aggregate_service

START_DATE, END_DATE = "2026-04-01", "2026-06-30"
st.set_page_config(page_title="Service | Kestrel", layout="wide")
st.title("Service Performance")
st.caption("Eligible delivered/partial orders; deleted, closed, test and migration outlets excluded")

data = service_orders(START_DATE, END_DATE)
region = st.sidebar.selectbox("Region", ["All"] + sorted(data.region.unique().tolist()))
basis = st.sidebar.radio("Quantity basis", ["Eaches", "Case Equivalent"])
if region != "All": data = data[data.region == region]
metric = "fill_rate_eaches" if basis == "Eaches" else "fill_rate_cases"

ordered = data.ordered_eaches.sum() if basis == "Eaches" else data.ordered_cases.sum()
delivered = data.delivered_eaches.sum() if basis == "Eaches" else data.delivered_cases.sum()
c1,c2,c3,c4=st.columns(4)
c1.metric("Fill rate",f"{delivered/ordered:.1%}" if ordered else "—")
c2.metric("OTIF",f"{data.otif.mean():.1%}" if len(data) else "—")
c3.metric("Eligible orders",f"{data.order_id.nunique():,}")
c4.metric("Orders >2h late",f"{data.loc[data.max_delay_minutes>120,'order_id'].nunique():,}")

dimension = st.selectbox("Compare by", ["region","warehouse","route_code","outlet_name","channel"])
summary = aggregate_service(data, dimension).sort_values(metric)
st.plotly_chart(px.bar(summary, x=dimension, y=metric, color="otif_rate", hover_data=["orders"], range_y=[0,1]), use_container_width=True)
st.subheader("Worst performers")
st.dataframe(summary[[dimension,metric,"otif_rate","orders"]].head(15), hide_index=True, use_container_width=True)

data["month"] = data.order_date.str[:7]
trend = aggregate_service(data, "month")
st.subheader("Monthly trend")
st.plotly_chart(px.line(trend, x="month", y=[metric,"otif_rate"], markers=True), use_container_width=True)

