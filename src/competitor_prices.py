import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRICE_FILE = ROOT / "data" / "competitor_prices.csv"


def normalize_name(value: str) -> str:
    text = value.lower()
    text = re.sub(r"combo|pack of 1|best before\s+\w+|family pack|\(new\)|selected|sel\.", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_prices() -> pd.DataFrame:
    if not PRICE_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(PRICE_FILE)


def match_prices(products: pd.DataFrame, listings: pd.DataFrame, threshold: float = 0.78) -> pd.DataFrame:
    if listings.empty:
        return pd.DataFrame()
    matches = []
    for listing in listings.itertuples(index=False):
        best = None
        for product in products.itertuples(index=False):
            name_score = SequenceMatcher(None, normalize_name(listing.title), normalize_name(product.product_name)).ratio()
            pack_score = float(str(listing.pack_uom).upper() == str(product.pack_size_uom).upper() and abs(float(listing.pack_size)-float(product.pack_size_value)) < 0.01)
            category_score = float(str(listing.category).lower() == str(product.category).lower())
            score = 0.75*name_score + 0.15*pack_score + 0.10*category_score
            if best is None or score > best[0]:
                best = (score, product)
        if best and best[0] >= threshold:
            product = best[1]
            row = listing._asdict()
            row.update({"product_id":product.product_id,"sku_code":product.sku_code,"product_name":product.product_name,"kestrel_mrp":product.mrp_inr,"match_confidence":best[0]})
            matches.append(row)
    return pd.DataFrame(matches)

