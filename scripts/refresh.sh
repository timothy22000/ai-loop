#!/usr/bin/env bash
# Refresh prices locally, on demand. Review the diff, then commit yourself.
set -euo pipefail
cd "$(dirname "$0")/.."

python -m pip install --quiet --upgrade yfinance
python scripts/refresh_prices.py
python scripts/build.py

echo
echo "Done. Review the changes:"
echo "    git diff data/"
echo "Commit when you're happy:"
echo "    git commit -am 'Refresh data'"
