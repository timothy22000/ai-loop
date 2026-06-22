# Contributing to The AI Loop

Thanks for helping keep the map accurate. The most useful contributions are **corrections, new deals, and status changes, with a source.**

## The golden rule: one source of truth

Never edit numbers inside `index.html`. All data lives in **`data/deals.json`**. After editing it, run the build:

```bash
python scripts/build.py
```

This regenerates the data block in `index.html` and the CSV exports, and validates your edit.

## Adding or changing a deal

Edges live in `deals.json` under `edges`:

```json
{ "from": "nvidia", "to": "openai", "kind": "Equity investment",
  "group": "invest", "amt": "Up to $100B", "status": "loi" }
```

- `from` / `to` must match an existing `id` in `nodes` (add a node first if needed).
- `group` is one of `invest` (gold), `spend` (teal), or `backstop` (red).
- `status` is one of:
  - `confirmed`, a signed, disclosed deal
  - `reported`, credible media reporting, not formally confirmed
  - `loi`, a letter of intent or non-binding commitment
  - `stalled`, announced but reportedly paused or unravelling
- Use `amt` for the short human label shown in the panel.

## What to include in a pull request or correction

1. The exact field(s) changing.
2. A **link to a primary source** (filing, company press release, or major outlet).
3. The date of the news.

Accuracy and honest status labels matter more than completeness. When in doubt, prefer the more conservative status.

## Style

- Keep labels short and factual. No hype.
- Distinguish reported from confirmed; do not upgrade a status without a source.
- The project avoids em dashes; use colons, commas or parentheses.
