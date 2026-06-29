#!/usr/bin/env python3
"""
Build step for The AI Loop.

Single source of truth: data/deals.json
This script injects that data into index.html (between the DATA markers) and
exports flat CSVs for analysis / a Hugging Face dataset.

Usage:
    python scripts/build.py

Workflow:
    1. Edit data/deals.json
    2. Run this script
    3. Commit the changes
"""
import json, re, csv, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "deals.json"
HTML = ROOT / "index.html"
ALLOWED_STATUS = {"confirmed", "reported", "loi", "stalled"}
ALLOWED_GROUP  = {"invest", "spend", "backstop"}

def load():
    return json.loads(DATA.read_text(encoding="utf-8"))

def validate(d):
    problems = []
    ids = {n["id"] for n in d["nodes"]}
    for e in d["edges"]:
        if e["from"] not in ids: problems.append(f"edge from unknown node: {e['from']}")
        if e["to"]   not in ids: problems.append(f"edge to unknown node: {e['to']}")
        if e["status"] not in ALLOWED_STATUS: problems.append(f"bad status '{e['status']}' on {e['from']}->{e['to']}")
        if e["group"]  not in ALLOWED_GROUP:  problems.append(f"bad group '{e['group']}' on {e['from']}->{e['to']}")
    if "</script" in json.dumps(d):
        problems.append("data contains the literal '</script' which would break the inline block")
    edgeset = {(e["from"], e["to"]) for e in d["edges"]}
    for L in d.get("loops", []):
        ns = L["nodes"]
        for i in range(len(ns)):
            pair = (ns[i], ns[(i + 1) % len(ns)])
            if pair not in edgeset:
                problems.append(f"loop '{L['id']}' references missing edge {pair[0]}->{pair[1]}")
    for s in d.get("supply", []):
        if s["from"] not in ids: problems.append(f"supply from unknown node: {s['from']}")
        if s["to"] not in ids:   problems.append(f"supply to unknown node: {s['to']}")
    return problems

def warnings(d):
    warns = []
    for e in d["edges"]:
        if not e.get("source"):
            warns.append(f"edge {e['from']}->{e['to']} has no source")
    for c in d["companies"]:
        if not c.get("source"):
            warns.append(f"company {c['company']} has no source (ok for price-only rows)")
    return warns

def inject(d):
    block = '<!-- DATA:START -->\n<script type="application/json" id="loop-data">\n' \
            + json.dumps(d, ensure_ascii=False, indent=2) \
            + '\n</script>\n<!-- DATA:END -->'
    html = HTML.read_text(encoding="utf-8")
    if "<!-- DATA:START -->" not in html:
        sys.exit("ERROR: DATA markers not found in index.html")
    html = re.sub(r"<!-- DATA:START -->.*?<!-- DATA:END -->", lambda m: block, html, flags=re.DOTALL)
    # keep the static "compiled" date spans in sync with the data (no-JS / crawlers)
    label = d["meta"].get("lastUpdatedLabel", "")
    for sid in ("meta-updated", "meta-updated-foot"):
        html = re.sub(rf'(id="{sid}">)[^<]*(<)', lambda m: m.group(1) + label + m.group(2), html)
    HTML.write_text(html, encoding="utf-8")

def export_csv(d):
    by_id = {n["id"]: n["name"] for n in d["nodes"]}
    with open(ROOT / "data" / "companies.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["company", "ticker", "cat", "price", "mktcap", "note", "source"])
        for c in d["companies"]:
            w.writerow([c["company"], c["ticker"], c.get("cat", ""), c["price"], c["mktcap"], c["note"], c.get("source", "")])
    with open(ROOT / "data" / "deals.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["investor_id", "recipient_id", "investor", "recipient",
                                       "kind", "group", "amount", "status", "verified", "source"])
        for e in d["edges"]:
            w.writerow([e["from"], e["to"], by_id.get(e["from"], e["from"]), by_id.get(e["to"], e["to"]),
                        e["kind"], e["group"], e["amt"], e["status"], e.get("verified", ""), e.get("source", "")])

def main():
    ap = argparse.ArgumentParser(description="Build The AI Loop from data/deals.json")
    ap.add_argument("--check", action="store_true",
                    help="verify index.html is in sync with deals.json (used in CI); make no changes")
    args = ap.parse_args()

    d = load()
    problems = validate(d)
    if problems:
        print("Validation failed:")
        for p in problems: print("  -", p)
        sys.exit(1)

    if args.check:
        expected = json.dumps(d, ensure_ascii=False, indent=2)
        html = HTML.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="loop-data">\n(.*?)\n</script>', html, re.DOTALL)
        if not m or m.group(1) != expected:
            sys.exit("Out of sync: run `python scripts/build.py` and commit the result.")
        label = d["meta"].get("lastUpdatedLabel", "")
        for sid in ("meta-updated", "meta-updated-foot"):
            ms = re.search(rf'id="{sid}">([^<]*)<', html)
            if ms and ms.group(1) != label:
                sys.exit(f"Out of sync: {sid} shows '{ms.group(1)}' but data says '{label}'. Run build.py.")
        print("Check OK: index.html is in sync with data/deals.json")
        return

    inject(d)
    export_csv(d)
    for w in warnings(d):
        print("  warning:", w)
    print(f"Built OK  |  {len(d['nodes'])} nodes, {len(d['edges'])} edges, {len(d['companies'])} companies")
    print(f"Last updated: {d['meta'].get('lastUpdatedLabel','?')}")
    print("Wrote: index.html, data/companies.csv, data/deals.csv")

if __name__ == "__main__":
    main()
