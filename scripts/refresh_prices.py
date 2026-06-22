#!/usr/bin/env python3
"""
Optional, best-effort price refresh for data/deals.json.

Pulls last price and market cap from Yahoo Finance via yfinance and rewrites the
matching rows in data/deals.json, then bumps meta.lastUpdated. After running it,
run scripts/build.py to regenerate the site and CSVs.

    pip install yfinance
    python scripts/refresh_prices.py
    python scripts/build.py

IMPORTANT
- This is best-effort. yfinance is an unofficial API and can break or return
  stale values. ALWAYS review the git diff before committing.
- Foreign listings (e.g. .KS) report market cap in local currency, so they are
  skipped here and kept manual. Private valuations (OpenAI, Anthropic, xAI) and
  any 'n/a' fields are never auto-touched.
"""
import json, datetime, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "deals.json"
SKIP_SUFFIXES = (".KS", ".KQ", ".T", ".TW")   # non-USD listings -> keep manual

def fmt_price(p):
    return f"~${p:,.0f}" if p else None

def fmt_cap(v):
    if not v: return None
    if v >= 1e12: return f"~${v/1e12:.2f}T"
    if v >= 1e9:  return f"~${v/1e9:.0f}B"
    return f"~${v/1e6:.0f}M"

def main():
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("Install yfinance first:  pip install yfinance")

    d = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    for c in d["companies"]:
        t = c["ticker"]
        if any(t.endswith(s) for s in SKIP_SUFFIXES):
            print(f"skip (manual): {t}"); continue
        try:
            info = yf.Ticker(t).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            cap   = info.get("marketCap")
        except Exception as ex:
            print(f"fetch failed: {t} ({ex})"); continue
        if price and c.get("price") != "n/a":
            np = fmt_price(price)
            if np and np != c["price"]: c["price"] = np; changed += 1
        if cap and c.get("mktcap") != "n/a":
            nc = fmt_cap(cap)
            if nc and nc != c["mktcap"]: c["mktcap"] = nc; changed += 1
        print(f"updated: {t:12} {c['price']:10} {c['mktcap']}")

    today = datetime.date.today()
    d["meta"]["lastUpdated"] = today.isoformat()
    d["meta"]["lastUpdatedLabel"] = today.strftime("%-d %B %Y")
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{changed} field(s) changed. Now run:  python scripts/build.py")
    print("Review the diff before committing. Market caps and private valuations may still need manual edits.")

if __name__ == "__main__":
    main()
