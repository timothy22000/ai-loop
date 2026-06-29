#!/usr/bin/env python3
"""Validate data/deals.json and data/claims.json against their schemas.  Requires: pip install jsonschema"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    import jsonschema
except ImportError:
    sys.exit("Install jsonschema first:  pip install jsonschema")

schema = json.loads((ROOT / "schema" / "deals.schema.json").read_text(encoding="utf-8"))
data   = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))
jsonschema.validate(instance=data, schema=schema)

# referential integrity beyond what JSON Schema can express
ids = {n["id"] for n in data["nodes"]}
bad = [(e["from"], e["to"]) for e in data["edges"] if e["from"] not in ids or e["to"] not in ids]
if bad:
    sys.exit(f"Edges reference unknown nodes: {bad}")

# claim registry (non-deal figures): schema + source referential integrity
claims_schema = json.loads((ROOT / "schema" / "claims.schema.json").read_text(encoding="utf-8"))
claims = json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))
jsonschema.validate(instance=claims, schema=claims_schema)
src_ids = {s["id"] for s in claims["sources"]}
bad_refs = [(c["id"], sid) for c in claims["claims"] for sid in c.get("sourceIds", []) if sid not in src_ids]
if bad_refs:
    sys.exit(f"Claims reference unknown sources: {bad_refs}")

print(f"Schema valid: {len(data['nodes'])} nodes, {len(data['edges'])} edges, {len(data['companies'])} companies; "
      f"{len(claims['claims'])} claims / {len(claims['sources'])} sources.")
