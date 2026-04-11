#!/usr/bin/env python3
"""
Load Shawarma Stop customer-web menu into `products` / `categories`.

1. Clears existing menu data safely (nulls FKs on order_items & reviews, deletes cart/favorites/section links).
2. Removes all rows from `products` and `categories`.
3. Inserts categories + products from `seeds/shawarma_menu_products.json`.

Run from `shawarmabackend/` (with venv activated):

    python seed_shawarma_menu_from_json.py

Regenerate JSON after menu changes:

    python seeds/generate_menu_products_json.py
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

from sqlalchemy import text

# Ensure app imports work when run as script
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.models.menu import Category, MenuItem, MenuSectionItem  # noqa: E402
from app.models.user import CartItem, Favorite  # noqa: E402

NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def stable_product_id(frontend_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, f"shawarma-stop-menu-{frontend_id}"))


def seed_from_json(json_path: Path | None = None) -> None:
    path = json_path or (_ROOT / "seeds" / "shawarma_menu_products.json")
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Generate it with: python seeds/generate_menu_products_json.py"
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    categories_data = data["categories"]
    products_data = data["products"]

    db = SessionLocal()
    try:
        # --- detach FKs that block DELETE FROM products ---
        db.execute(text("UPDATE order_items SET menu_item_id = NULL WHERE menu_item_id IS NOT NULL"))
        db.execute(text("UPDATE reviews SET product_id = NULL WHERE product_id IS NOT NULL"))

        db.query(CartItem).delete()
        db.query(Favorite).delete()
        db.query(MenuSectionItem).delete()

        db.query(MenuItem).delete()
        db.query(Category).delete()
        db.commit()

        # --- insert categories ---
        for c in categories_data:
            db.add(
                Category(
                    id=c["id"],
                    name=c["name"],
                    description=c.get("description") or "",
                )
            )
        db.commit()

        # --- insert products ---
        for p in products_data:
            fid = str(p["frontendId"])
            pid = stable_product_id(fid)
            images = None
            if p.get("image2"):
                images = [p["image"], p["image2"]]
            item = MenuItem(
                id=pid,
                name=p["name"],
                category_id=p["categoryId"],
                price=float(p["price"]),
                description=p.get("description") or "",
                image=p.get("image"),
                images=images,
                status="Available",
                is_available=True,
                rating=0.0,
                reviews_count=0,
                order_count=0,
            )
            db.add(item)

        db.commit()

        n_cat = db.query(Category).count()
        n_prod = db.query(MenuItem).count()
        print(f"OK: seeded {n_cat} categories and {n_prod} products from {path.name}")
        print("Sample product IDs (stable uuid5):")
        for sample_fid in ("1", "21", "41"):
            print(f"   frontendId={sample_fid} -> {stable_product_id(sample_fid)}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


def main() -> None:
    seed_from_json()


if __name__ == "__main__":
    main()
