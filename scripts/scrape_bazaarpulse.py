import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://localhost:8080"
START_PATHS = ["/city/mumbai/page/1.html","/city/delhi/page/1.html","/city/bengaluru/index.html","/city/chennai/index.html"]


def number(text):
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    return float(match.group(1)) if match else None


def parse_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("div.product-item"):
        link = card.select_one("a[href*='/product/']")
        muted = card.select("div.muted")
        price_node = card.select_one(".price, .sellingPrice, .amt, .pricing-block")
        if not link or not muted or not price_node:
            continue
        parts = [x.strip() for x in muted[0].get_text(" ", strip=True).split("·")]
        if len(parts) < 3:
            continue
        pack_match = re.search(r"([0-9.]+)\s*([a-zA-Z]+)", parts[1])
        mrp_node = next((x for x in muted if "MRP" in x.get_text()), None)
        last_seen = next((x for x in muted if "Last seen:" in x.get_text()), None)
        if not pack_match or not mrp_node:
            continue
        current_price = (
            float(price_node.get("data-price-paise")) / 100
            if price_node.get("data-price-paise") else number(price_node.get_text(" ", strip=True))
        )
        rows.append({
            "listing_id": card.get("data-listing-id"), "title": link.get_text(" ", strip=True),
            "retailer": parts[0], "pack_size": float(pack_match.group(1)), "pack_uom": pack_match.group(2).upper(),
            "category": parts[2], "current_price": current_price,
            "listed_mrp": number(mrp_node.get_text(" ", strip=True)),
            "in_stock": "unavailable" not in mrp_node.get_text(" ", strip=True).lower(),
            "last_seen": last_seen.get_text().split(":",1)[1].strip() if last_seen else None,
            "detail_url": urljoin(page_url, link["href"]),
        })
    links = []
    for anchor in soup.select(".pager a[href]"):
        link = urljoin(page_url, anchor["href"])
        parsed = urlparse(link)
        page_number = parse_qs(parsed.query).get("p", [None])[0]
        if page_number and parsed.path.endswith("/index.html"):
            path = parsed.path.replace("/index.html", f"/index_p{page_number}.html")
            link = urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
        links.append(link)
    return rows, links


def main():
    robots = RobotFileParser(urljoin(BASE_URL, "/robots.txt")); robots.read()
    queue = [urljoin(BASE_URL, p) for p in START_PATHS]; seen=set(); rows=[]
    with requests.Session() as session:
        while queue:
            url=queue.pop(0)
            if url in seen or not robots.can_fetch("KestrelControlTower/1.0", url):
                continue
            seen.add(url); response=session.get(url, timeout=15); response.raise_for_status()
            page_rows, links=parse_page(response.text,url)
            city=urlparse(url).path.split("/")[2]
            for row in page_rows: row["city"]={"delhi":"Delhi NCR"}.get(city,city.title())
            rows.extend(page_rows)
            queue.extend(x for x in links if x not in seen)
            time.sleep(1)
    output=ROOT/"data"/"competitor_prices.csv"
    result = pd.DataFrame(rows).drop_duplicates("listing_id")
    result.to_csv(output,index=False)
    print(f"Saved {len(result)} unique listings to {output}")


if __name__ == "__main__": main()
