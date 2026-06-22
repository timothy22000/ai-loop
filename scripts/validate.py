#!/usr/bin/env python3
"""Validate data/deals.json against schema/deals.schema.json.  Requires: pip install jsonschema"""
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
print(f"Schema valid: {len(data['nodes'])} nodes, {len(data['edges'])} edges, {len(data['companies'])} companies.")
