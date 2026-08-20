# Kestrel Provisions Supply Chain Control Tower

A Streamlit control tower that answers two operational questions:

1. Where is customer service failing?
2. Where is money leaking?

The application combines operational data from SQLite, billed freight from the supplied partner API, and competitor prices scraped from the supplied BazaarPulse website.

## What is included

- **Executive:** FY2026–27 Q1 KPIs and outlets requiring attention
- **Service:** fill rate in eaches or case equivalents and order-level OTIF
- **Cold Chain:** temperature excursions, cold-chain returns, and near-expiry exposure
- **Financial Leakage:** returns, credit notes, and actual billed freight per delivered case
- **Price Position:** Kestrel MRP compared with the lowest in-stock competitor price

Regional, warehouse, route, outlet, category, carrier, and city filters are provided where supported by the source data.

## Required assignment assets

The following supplied assets must exist in the project:

```text
data/kestrel_ops.db
partner_api/server.py
bazaarpulse_site/
```

The database is intentionally excluded from Git. Copy the supplied database into `data/kestrel_ops.db` after cloning the repository. Do not create an empty database file.

The generated `data/competitor_prices.csv` is also excluded from Git because the scraper can reproduce it.

## Cold-start setup on Windows

Open the repository folder in VS Code and select **Terminal > New Terminal**.

```powershell
git clone https://github.com/siddharthranjan456/kestrel-supply-chain-control-tower.git
cd .\kestrel-supply-chain-control-tower

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy the supplied database to:

```text
<repository>\data\kestrel_ops.db
```

Verify that it exists and is not empty:

```powershell
Get-Item .\data\kestrel_ops.db | Select-Object FullName, Length
```

Run the tests:

```powershell
python -m pytest -q
```

## Run the complete system

The three services must run in separate VS Code terminals. Run all commands from the repository root.

### Terminal 1 — BazaarPulse website

```powershell
.\.venv\Scripts\Activate.ps1
python -m http.server 8080 --bind 127.0.0.1 --directory .\bazaarpulse_site
```

Verify it at `http://127.0.0.1:8080`.

### Terminal 2 — freight partner API

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn partner_api.server:app --host 127.0.0.1 --port 8088
```

Verify it at:

- Health: `http://127.0.0.1:8088/v1/health`
- API documentation: `http://127.0.0.1:8088/docs`

The API root `/` is not implemented, so `http://127.0.0.1:8088/` returning `404 Not Found` is expected. `0.0.0.0` is a server binding address and should not be entered in the browser.

### Terminal 3 — competitor scrape and dashboard

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\scrape_bazaarpulse.py
python -m streamlit run .\app.py
```

Open the dashboard at `http://localhost:8501`.

The scraper should create:

```text
data/competitor_prices.csv
```

The scrape only needs to be repeated when the supplied BazaarPulse content changes or the generated CSV is removed.

## Data and metric rules

- The default reporting period is FY2026–27 Q1: 1 April through 30 June 2026.
- Fill rate defaults to eaches because customers penalise unit shortages. A case-equivalent view is also available.
- Mixed units of measure are normalised using `case_pack_at_order`.
- OTIF is calculated at order level. An order is OTIF only when it is on time and delivered in full.
- Service KPIs exclude cancelled/open orders and deleted, closed, test, or migration outlets.
- Return quantities use their absolute value because one source reverses the sign.
- Temperature excursions use the delivery-level excursion flag supplied in the database.
- Near-expiry exposure uses the latest available inventory snapshot on or before the period end.
- Billed freight comes from the supplied partner API, is cursor-paginated, retries temporary failures, and converts paise to rupees.
- Competitor matches are normalised by product name, pack, and category and are excluded when confidence is below the configured threshold.

## Troubleshooting

### Unable to load operational data

Confirm that the real supplied database exists at `data/kestrel_ops.db` and has a non-zero file size:

```powershell
Get-Item .\data\kestrel_ops.db | Select-Object FullName, Length
```

### No scrape output found

Keep Terminal 1 running, then execute from the repository root:

```powershell
python .\scripts\scrape_bazaarpulse.py
```

### Address invalid for port 8088

Use `http://127.0.0.1:8088/docs`, not `http://0.0.0.0:8088`.

### Port already in use

Stop the previous process in the corresponding terminal with `Ctrl+C`, then start it again.

## Known limitations

- The plain-English Ask Anything capability is not included; the rationale is documented in `DECISIONS.md`.
- The application has no authentication or role-based access control. Regional views are implemented through filters.
- Carrier invoices do not contain a delivery ID, so freight per case is reliable at warehouse level rather than individual-delivery level.
- Competitor matching is confidence-gated and uncertain matches require manual review.
- The submission uses a fixed FY2026–27 Q1 scope because the board requirement explicitly prioritises Q1.

See `DECISIONS.md` for assumptions, trade-offs, production risks, and proposed next steps.
