# Decisions

**Built.** A five-page Streamlit control tower for FY2026–27 Q1 covering service, cold chain, near-expiry exposure, returns/credit notes, billed freight, and competitor price position. SQLite supplies operational truth; billed freight comes only from the supplied partner API; competitor prices come only from the supplied BazaarPulse site.

**Definitions.** Fill rate defaults to eaches because customers penalise unit shortages; the UI also offers case equivalents. Mixed UOM lines are normalised with `case_pack_at_order`. OTIF is evaluated at order level: the maximum delivery delay is non-positive and total delivered eaches meet total ordered eaches. Cancelled/open orders and deleted, closed, test, or migration outlets are excluded from service KPIs. Returns use absolute quantity because one source reverses the sign.

**Cold chain.** Excursions use `deliveries.temperature_excursion_flag`; there is no sensor-reading table. Near-expiry uses the latest weekly snapshot on or before the selected period end. Value exposure is available cases × current case pack × current list price and is clearly labelled estimated trade value, not accounting cost.

**External data.** Freight calls are date-scoped, cursor-paginated, convert paise to rupees, and retry 429/503 responses. Freight per case is reliable at warehouse level; carrier-level cost is shown without inventing a delivery-to-carrier allocation. BazaarPulse crawling respects robots.txt and its crawl delay, supports its inconsistent pagination/price markup, and excludes low-confidence product matches.

**Not built.** Unrestricted LLM-to-SQL, weather/holiday enrichment, and automated background ingestion were omitted to keep the submission small and defensible. A production version would materialise governed metric tables, schedule external ingestion, store match-review decisions, add authentication/RBAC, monitoring, data contracts, and incremental processing. At 100× volume, repeated SQLite scans and in-process caches fail first; move transforms to a warehouse and serve pre-aggregated datasets.

