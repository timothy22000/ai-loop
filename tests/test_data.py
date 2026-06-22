import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))

def test_edges_reference_real_nodes():
    ids = {n["id"] for n in D["nodes"]}
    for e in D["edges"]:
        assert e["from"] in ids, e
        assert e["to"] in ids, e

def test_status_and_group_enums():
    for e in D["edges"]:
        assert e["status"] in {"confirmed", "reported", "loi", "stalled"}, e
        assert e["group"] in {"invest", "spend", "backstop"}, e

def test_every_deal_is_sourced():
    for e in D["edges"]:
        assert e.get("source", "").startswith("http"), e
        assert e.get("verified"), e

def test_no_em_dashes_in_data():
    assert "\u2014" not in json.dumps(D, ensure_ascii=False)

def test_every_company_has_a_category():
    for c in D["companies"]:
        assert c.get("cat"), c

def test_loops_map_to_real_edges():
    edgeset = {(e["from"], e["to"]) for e in D["edges"]}
    ids = {n["id"] for n in D["nodes"]}
    for L in D.get("loops", []):
        ns = L["nodes"]
        assert len(ns) >= 2, L
        for nid in ns:
            assert nid in ids, (L["id"], nid)
        for i in range(len(ns)):
            pair = (ns[i], ns[(i + 1) % len(ns)])
            assert pair in edgeset, (L["id"], pair)

def test_supply_links_map_to_real_nodes():
    ids = {n["id"] for n in D["nodes"]}
    for s in D.get("supply", []):
        assert s["from"] in ids, s
        assert s["to"] in ids, s
        assert s.get("kind"), s
