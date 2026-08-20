# Decisions

## What I built

I built a five-page Streamlit supply-chain control tower for FY2026–27 Q1. It covers service performance, cold-chain failures, near-expiry inventory, returns and credit notes, billed freight, and competitor price position. SQLite is the operational source of truth. Actual billed freight comes only from the supplied partner API, while competitor prices come only from the supplied BazaarPulse site. Regional managers can narrow the same governed views using filters rather than maintaining separate reports.

I prioritised a small working system with traceable metric definitions over attempting every requested feature. The database and reproducible scrape output are excluded from Git; setup and startup commands are documented in `README.md`.

## Assumptions and ambiguous requirements

The brief conflicts on fill-rate units: Supply Chain requests cases while Sales requests eaches. The dashboard therefore defaults to eaches because customer penalties are based on units short, but it also provides case-equivalent fill rate for the operational team. Mixed-UOM lines are normalised using `case_pack_at_order`.

OTIF is calculated at order level: the greatest delivery delay must be zero or less and total delivered eaches must meet total ordered eaches. Cancelled/open orders and deleted, closed, test, or migration outlets are excluded from service KPIs. Return quantities use absolute values because one source records reversals with the opposite sign.

Temperature excursions use `deliveries.temperature_excursion_flag` because no sensor-reading table is supplied. Near-expiry uses the latest weekly snapshot on or before the period end. Exposure is available cases multiplied by the current case pack and list price; it is labelled estimated trade value rather than accounting cost.

Freight requests are date-scoped and cursor-paginated, convert paise to rupees, and retry 429/503 responses. Because invoices lack a delivery ID, freight per delivered case is reported reliably at warehouse level without inventing a delivery-to-carrier allocation. BazaarPulse crawling follows its robots instructions and crawl delay, handles inconsistent pagination and price markup, and excludes low-confidence product matches.

## What I deliberately did not build

I did not build the requested plain-English Ask Anything capability. Direct LLM-to-SQL would introduce correctness, security, and metric-consistency risks that could not be addressed properly within the assignment time. I chose tested calculations and visible filters instead. I also omitted authentication/RBAC, automated background ingestion, weather/holiday enrichment, and unrestricted date-period configuration.

## What I would do with two more weeks

I would add scheduled and incremental ingestion, governed metric tables, data contracts and quality alerts, authentication with regional access rules, monitoring, persisted product-match review decisions, and broader date controls. I would implement Ask Anything through a constrained semantic layer containing approved metrics, read-only query templates, result validation, citations, and audit logs rather than allowing unrestricted SQL generation.

## What breaks first in production

At 100× data volume, repeated SQLite scans and in-process Pandas transformations would fail first, followed by Streamlit cache and single-process limits. I would move transformations into a warehouse, materialise tested aggregates, schedule ingestion independently, and serve the dashboard through an authenticated application/API layer. External API rate limits and scraper markup changes would require durable queues, checkpoints, monitoring, and contract tests.
