#!/usr/bin/env python3
"""
Legacy entrypoint name kept for scripts/CI.

Previously ran `fresh_products_data.sql` on SQLite only. Now applies the Shawarma Stop
customer-web menu from JSON (see `seeds/shawarma_menu_products.json`).

Run from `shawarmabackend/`:

    python run_fresh_products.py

Regenerate menu JSON from the same source as the Next.js menu (`menuItems.ts`):

    python seeds/generate_menu_products_json.py
"""

from seed_shawarma_menu_from_json import seed_from_json


def run_fresh_products() -> None:
    seed_from_json()


if __name__ == "__main__":
    run_fresh_products()
