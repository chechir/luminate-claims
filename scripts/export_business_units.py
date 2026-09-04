#!/usr/bin/env python3
"""Page through GET /business_units (50/page, per total_results) and write
every record to data/business_units.parquet. Nested fields (effective_period)
are kept as structs, not flattened. Run: python scripts/export_business_units.py
"""

import time
from pathlib import Path

import pandas as pd
from helpers import MUSICAL_RIGHTS_URL, authenticate, get, load_credentials
from loguru import logger

BUSINESS_UNITS_URL = f"{MUSICAL_RIGHTS_URL}/business_units"
PAGE_SIZE = 50
# 1 r/s account limit (see helpers.py) — a tighter loop 404s instead of
# 429ing, so throttle here rather than retry on failure.
REQUEST_INTERVAL_SECONDS = 1.1
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "business_units.parquet"


def main() -> None:
    api_key, username, password = load_credentials()
    token = authenticate(api_key, username, password)

    records = fetch_all_business_units(api_key, token)
    logger.info(f"fetched {len(records)} business units")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    pd.DataFrame(records).to_parquet(OUTPUT_PATH, engine="pyarrow")
    logger.success(f"wrote {OUTPUT_PATH}")


def fetch_all_business_units(api_key: str, token: str) -> list[dict]:
    records: list[dict] = []
    offset = 0
    while True:
        page = fetch_page(api_key, token, offset)
        records.extend(page["business_units"])
        logger.debug(f"from={offset} -> {len(page['business_units'])} records")
        offset += PAGE_SIZE
        if offset >= page["total_results"]:
            return records
        time.sleep(REQUEST_INTERVAL_SECONDS)


def fetch_page(api_key: str, token: str, offset: int) -> dict:
    response = get(
        BUSINESS_UNITS_URL, api_key, token, params={"from": offset, "size": PAGE_SIZE}
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    main()
