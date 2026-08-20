# Kestrel Provisions Supply Chain Control Tower

A working Streamlit control tower answering two questions: where customer service is failing and where money is leaking.

## Source files from the assignment pack

Keep these supplied assets in the repository working tree (the database remains gitignored):

```text
data/kestrel_ops.db
partner_api/server.py
bazaarpulse_site/
```

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

## Run operational dashboard

```powershell
python -m streamlit run app.py
```

Open `http://localhost:8501`.

## Enable billed freight

In a second PowerShell window:

```powershell
.\.venv\Scripts\Activate.ps1
python .\partner_api\server.py
```

The Financial Leakage page requests Q1 invoices from `http://localhost:8088`, follows every cursor, retries 429/503 responses, and converts paise to rupees.

## Enable competitor prices

In a second terminal:

```powershell
cd .\bazaarpulse_site
python -m http.server 8080
```

In the project-root terminal:

```powershell
python .\scripts\scrape_bazaarpulse.py
```

The scraper writes `data/competitor_prices.csv`. Return to the project root and restart Streamlit. The generated CSV is ignored by Git because it is reproducible from the supplied site.

## Pages

- Executive: Q1 KPIs and immediate-attention outlets
- Service: eaches/case fill rate and order-level OTIF
- Cold Chain: excursions, cold-chain returns, and 30-day near-expiry exposure
- Financial Leakage: credit notes and actual billed freight per delivered case
- Price Position: Kestrel MRP versus lowest in-stock competitor price for top-value SKUs

## Known limitations

Carrier invoices have warehouse/route/date keys but no delivery ID, so freight per case is reported at warehouse level. Competitor matching is deliberately confidence-gated. The dashboard uses a fixed FY2026–27 Q1 scope because the board requirement explicitly prioritises Q1.

