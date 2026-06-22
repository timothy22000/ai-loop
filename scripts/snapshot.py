#!/usr/bin/env python3
"""
Save a dated snapshot of the dataset under data/snapshots/<date>/ so the
evolution of the loop is preserved over time. Run after a meaningful update.

    python scripts/snapshot.py
"""
import json, shutil, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))
date = d.get("meta", {}).get("lastUpdated") or datetime.date.today().isoformat()
out = ROOT / "data" / "snapshots" / date
out.mkdir(parents=True, exist_ok=True)
for f in ["deals.json", "companies.csv", "deals.csv"]:
    src = ROOT / "data" / f
    if src.exists():
        shutil.copy(src, out / f)
print("Snapshot written to", out.relative_to(ROOT))
