---
license: cc-by-4.0
language:
  - en
pretty_name: "The AI Loop: Circular Economy of AI"
tags:
  - finance
  - ai-industry
  - data-visualization
  - knowledge-graph
configs:
  - config_name: deals
    data_files: deals.csv
  - config_name: companies
    data_files: companies.csv
---

# The AI Loop dataset

A small, hand-curated dataset mapping the **circular economy of the AI industry**: who invests in whom, who buys it back, and at what reported scale. It powers the interactive site at [The AI Loop](https://github.com/) (add your link) and is published here for reuse.

Current through **June 2026**. This is desk research from public reporting, not original reporting.

## Files

### `deals.csv`: the money loop (one row per directed flow)
| column | meaning |
|---|---|
| `investor_id`, `recipient_id` | node ids for the two parties |
| `investor`, `recipient` | display names |
| `kind` | short description of the flow |
| `group` | `invest` (capital in), `spend` (chips/cloud back), or `backstop` |
| `amount` | reported headline figure (text, e.g. "Up to $100B") |
| `status` | `confirmed`, `reported`, `loi` (letter of intent), or `stalled` |
| `verified` | date of the cited source (ISO) |
| `source` | primary announcement or major-outlet URL |

### `companies.csv`: the connected public companies
| column | meaning |
|---|---|
| `company`, `ticker` | name and exchange ticker |
| `price`, `mktcap` | dated snapshot (mid-June 2026); `n/a` where not tracked |
| `note` | role in the loop |
| `source` | primary source for the company's role, where available |

The canonical source of truth is `deals.json` (graph + tables + metadata). The CSVs are generated from it by `scripts/build.py`.

## How to read `status`
`confirmed` is a signed, disclosed deal. `reported` is credible reporting, not formally confirmed. `loi` is a non-binding commitment. `stalled` was announced, then reportedly paused. The label reflects the latest reporting, not the cited source alone.

## License
**CC BY 4.0.** Reuse freely with attribution. Prices are snapshots, not investment advice.
