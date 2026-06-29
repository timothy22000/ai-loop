import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))

VALID_STATUSES = {"verified", "reported", "estimate", "contested", "uncertain", "needs_update"}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_SECTIONS = {
    "tape", "debate", "materials", "concentration", "lookthrough",
    "deal_context", "correction_watchlist", "methodology",
}


def test_source_ids_are_unique():
    ids = [s["id"] for s in CLAIMS["sources"]]
    assert len(ids) == len(set(ids))


def test_claim_ids_are_unique():
    ids = [c["id"] for c in CLAIMS["claims"]]
    assert len(ids) == len(set(ids))


def test_claim_source_references_exist():
    source_ids = {s["id"] for s in CLAIMS["sources"]}
    for claim in CLAIMS["claims"]:
        for sid in claim.get("sourceIds", []):
            assert sid in source_ids, (claim["id"], sid)


def test_claim_status_confidence_and_section_enums():
    for claim in CLAIMS["claims"]:
        assert claim["status"] in VALID_STATUSES, claim
        assert claim["confidence"] in VALID_CONFIDENCE, claim
        assert claim["section"] in VALID_SECTIONS, claim


def test_hard_verified_claims_have_sources():
    for claim in CLAIMS["claims"]:
        if claim["status"] == "verified":
            assert claim.get("sourceIds"), claim
            assert claim["confidence"] in {"high", "medium"}, claim


def test_uncertain_or_needs_update_claims_are_not_high_confidence_without_notes():
    for claim in CLAIMS["claims"]:
        if claim["status"] in {"uncertain", "needs_update"}:
            assert claim["notes"], claim
            if claim["status"] == "uncertain":
                assert claim["confidence"] in {"low", "medium"}, claim


def test_no_em_dashes_in_claim_data():
    assert "\u2014" not in json.dumps(CLAIMS, ensure_ascii=False)


def test_inline_citations_trace_to_registry():
    """Every inline citation (class="cite") in the site must resolve to a source
    in the claim registry, so the registry stays the single source of truth."""
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    cite_urls = re.findall(r'<a class="cite" href="([^"]+)"', html)
    assert cite_urls, "no inline citations found in index.html"
    src_urls = {s["url"] for s in CLAIMS["sources"]}
    missing = sorted({u for u in cite_urls if u not in src_urls})
    assert not missing, f"inline citations missing from claim registry: {missing}"
