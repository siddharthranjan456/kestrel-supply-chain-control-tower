import plotly.express as px
import streamlit as st
from src.analytics import top_skus
from src.competitor_prices import load_prices, match_prices

START_DATE,END_DATE="2026-04-01","2026-06-30"
st.set_page_config(page_title="Price Position | Kestrel",layout="wide")
st.title("Competitor Price Position")
listings=load_prices()
if listings.empty:
    st.warning("No scrape output found. Start BazaarPulse on port 8080, then run scripts/scrape_bazaarpulse.py.")
    st.stop()
products=top_skus(START_DATE,END_DATE,20)
matches=match_prices(products,listings)
if matches.empty:
    st.error("No high-confidence product matches were found.")
    st.stop()
city=st.selectbox("City",sorted(matches.city.unique()))
filtered=matches[(matches.city==city)&(matches.in_stock.astype(str).str.lower().isin(["true","1"]))]
best=filtered.groupby(["product_id","sku_code","product_name","kestrel_mrp"],as_index=False).agg(lowest_competitor_price=("current_price","min"),match_confidence=("match_confidence","max"))
best["price_gap_inr"]=best.kestrel_mrp-best.lowest_competitor_price
best["price_gap_pct"]=100*best.price_gap_inr/best.lowest_competitor_price
st.metric("Matched top-20 SKUs",f"{best.product_id.nunique()} / 20")
st.plotly_chart(px.bar(best.sort_values("price_gap_pct"),x="product_name",y="price_gap_pct",color="price_gap_pct",labels={"price_gap_pct":"Kestrel MRP gap (%)"}),use_container_width=True)
st.dataframe(best.sort_values("price_gap_pct",ascending=False),hide_index=True,use_container_width=True)

