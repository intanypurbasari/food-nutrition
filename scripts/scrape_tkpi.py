from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import DEFAULT_LIMIT, MAX_LIMIT_WITHOUT_OVERRIDE
from src.scrapers.tkpi_scraper import scrape_tkpi


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape TKPI with conservative academic settings.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--allow-large-limit", action="store_true")
    args = parser.parse_args()

    if args.limit > MAX_LIMIT_WITHOUT_OVERRIDE and not args.allow_large_limit:
        print(f"Refusing limit {args.limit}. Use --allow-large-limit explicitly for values above {MAX_LIMIT_WITHOUT_OVERRIDE}.")
        return 2

    result = scrape_tkpi(limit=max(args.limit, 0))
    print(f"TKPI rows written: {len(result.rows)}")
    if result.errors:
        print("TKPI completed with warnings/errors. See reports/tkpi_scrape_errors.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
