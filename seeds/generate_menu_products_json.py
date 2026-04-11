#!/usr/bin/env python3
"""
One-off / repeatable generator: writes shawarma_menu_products.json from the same
product list as Shawarma Stop `src/lib/menuItems.ts` + image URLs from `menuAssets.ts`.
Run from repo root: python shawarmabackend/seeds/generate_menu_products_json.py
"""
from __future__ import annotations

import json
from pathlib import Path

# Figma MCP asset URLs (mirror Shawarma Stop src/lib/menuAssets.ts)
FIGMA = {
    "food261": "https://www.figma.com/api/mcp/asset/9121e3b7-8913-4a2f-b6bb-69a35610ba9e",
    "food262": "https://www.figma.com/api/mcp/asset/076ef111-d16b-4b4d-b751-f1489c7f0f0a",
    "ellipse1451": "https://www.figma.com/api/mcp/asset/2a2a9798-5b27-4f9e-a805-5e5c85de4202",
    "food263": "https://www.figma.com/api/mcp/asset/f2afc747-d16c-4484-b4fb-74adb83b4b79",
    "food264": "https://www.figma.com/api/mcp/asset/8189cb44-cfce-43d1-b86a-6782e0325127",
    "food265": "https://www.figma.com/api/mcp/asset/99a8c1d6-799d-450e-a11b-70dbf30ca6a9",
    "food266": "https://www.figma.com/api/mcp/asset/d0eaf985-a626-4787-976e-24c345bdbbe2",
    "food267": "https://www.figma.com/api/mcp/asset/efb44d0d-fdb8-4c20-a3e6-6bebc5b47a42",
    "food268": "https://www.figma.com/api/mcp/asset/e8152eb8-5cde-4ad8-91bc-ebd6c04289b0",
    "food269": "https://www.figma.com/api/mcp/asset/57b083b0-38bd-4312-a2ed-c005f337522b",
    "food270": "https://www.figma.com/api/mcp/asset/fada7817-50e0-4271-a9f4-517ec84bad92",
    "food271": "https://www.figma.com/api/mcp/asset/bcd56128-85ec-4588-a760-fb929a9ba1a3",
    "food272": "https://www.figma.com/api/mcp/asset/79312ee2-2995-4a3f-99d1-fbd857702fe7",
    "food273": "https://www.figma.com/api/mcp/asset/23e34629-168a-4e61-aa9a-26db762a68b8",
    "food274": "https://www.figma.com/api/mcp/asset/ea5c82c2-f184-409b-8a3a-82031025a1c7",
    "food275": "https://www.figma.com/api/mcp/asset/7d84c387-b464-4cd5-9946-5115e7146b26",
    "food276": "https://www.figma.com/api/mcp/asset/b591886b-eea3-4003-92b5-4bf05ae8b91e",
    "food277": "https://www.figma.com/api/mcp/asset/41cfe949-2907-477d-8428-e9fde16ad34c",
    "food278": "https://www.figma.com/api/mcp/asset/43ae4389-c3ea-4687-b21e-9c352813740b",
    "food279": "https://www.figma.com/api/mcp/asset/a8d677db-c0b5-40f7-9791-f8b890d0b20b",
    "food280": "https://www.figma.com/api/mcp/asset/c2213e35-362e-47de-b7b1-6e9fc93669f3",
    "food281": "https://www.figma.com/api/mcp/asset/9f090e78-6f83-4077-9bcc-17993545d67c",
    "food282": "https://www.figma.com/api/mcp/asset/a0fc6412-545e-4151-8f1e-44575bbc920c",
    "food283": "https://www.figma.com/api/mcp/asset/d82cbb44-8f87-4cae-aa72-e799a4af81df",
    "food284": "https://www.figma.com/api/mcp/asset/edf02ebb-b7d0-459b-afb5-13fd33802a2f",
    "food285": "https://www.figma.com/api/mcp/asset/f2502a95-01e2-4a28-b2f1-236b26eff873",
    "food286": "https://www.figma.com/api/mcp/asset/b6f1ab65-7c0f-4690-8f91-d19bb9c4b08f",
    "food288": "https://www.figma.com/api/mcp/asset/1dcf6bb5-b3b8-431d-9df0-3e362de38c3f",
    "food289": "https://www.figma.com/api/mcp/asset/71d97e94-8eb4-4765-b8c3-a5cabc168a01",
    "food290": "https://www.figma.com/api/mcp/asset/32426eb4-f9db-40db-909d-0eb75b3657bc",
    "food291": "https://www.figma.com/api/mcp/asset/35f0c86a-f15a-4d75-8cb8-5c85320f1d84",
    "food292": "https://www.figma.com/api/mcp/asset/a1c9be51-8d39-4327-aff6-d9d8b56a3cdf",
    "food293": "https://www.figma.com/api/mcp/asset/57eb0b30-ffa2-4e38-9e60-b0ece8dc1718",
    "food294": "https://www.figma.com/api/mcp/asset/63eea26e-429f-4751-9127-c6f1bc5f4ea2",
    "food295": "https://www.figma.com/api/mcp/asset/499cefbb-244a-47b9-aa18-316da95c93d6",
    "food296": "https://www.figma.com/api/mcp/asset/608d38eb-1438-4fd0-99fc-bb757e82e9a2",
    "food297": "https://www.figma.com/api/mcp/asset/7b8c6e9b-812d-4651-9c42-107c0538635e",
}

# (frontendId, category, name, description, price_pkr, image_key, badge?, image2_key?)
# Matches Shawarma Stop src/lib/menuItems.ts row-for-row.
ROWS: list[tuple] = [
    ("1", "Appetizers", "Hummus", "Velvety, protein-rich hummus crafted from simple, wholesome ingredients.", 495, "food261", "Single", None),
    ("2", "Appetizers", "Hummus with Shawarma Chicken", "Creamy hummus topped with tender, spiced shawarma chicken", 825, "food262", "Single", None),
    ("3", "Appetizers", "Fattoush Salad", "A fresh mix of crisp vegetables, toasted pita, and tangy lemon-sumac dressing.", 385, "ellipse1451", None, None),
    ("4", "Appetizers", "Hummus", "Velvety, protein-rich hummus crafted from simple, wholesome ingredients.", 825, "food261", "Family", None),
    ("5", "Appetizers", "Hummus with Shawarma Chicken", "Creamy hummus topped with tender, spiced shawarma chicken", 1155, "food262", "Family", None),
    ("6", "Appetizers", "Fattoush Salad", "A fresh mix of crisp vegetables, toasted pita, and tangy lemon-sumac dressing.", 605, "food263", "Single", None),
    ("7", "Appetizers", "Fattoush Chicken Shawarma Fries", "A flavorful fusion of crispy fries, spiced chicken shawarma.", 605, "food264", "Single", None),
    ("8", "Appetizers", "Fattoush Chicken Shawarma Fries", "A flavorful fusion of crispy fries, spiced chicken shawarma.", 825, "food264", "Family", None),
    ("9", "Appetizers", "Fries", "Crispy golden fries, perfectly seasoned and freshly cooked for a satisfying crunch.", 220, "food265", "Regular", None),
    ("10", "Appetizers", "Masala Fries", "Crispy golden fries dusted with a rich, aromatic masala blend and extra crunch.", 242, "food266", "Regular", None),
    ("11", "Appetizers", "Chipotle Cheezy Fries", "Crunchy fries loaded with creamy cheese and bold, smoky chipotle flavor.", 605, "food267", "Regular", None),
    ("12", "Appetizers", "Loaded Shawarma Fries", "Loaded fries with tender shawarma chicken, sauces, and Middle Eastern spices.", 715, "food268", "Regular", None),
    ("13", "Appetizers", "Falafel (7 pieces)", "Crispy-on-the-outside, soft-inside falafel made with herbs and spices (7 pieces).", 825, "food269", "Regular", None),
    ("14", "Fatayers", "Pepperoni Fatayer", "Fatayer with a twist, stuffed with pepperoni and cheese, baked to golden perfection.", 825, "food270", "Single", None),
    ("15", "Fatayers", "Zaatar Cheese Fatayer", "Zaatar and melted cheese combined in a savory pastry, baked until perfectly golden.", 825, "food271", "Single", None),
    ("16", "Fatayers", "Shawarma Arabi", "Shawarma rolled in flatbread, sliced and served with garlic sauce.", 1155, "food272", "Regular", None),
    ("17", "Fatayers", "Cheese Fatayer", "Baked pastry filled with a blend of soft cheeses, perfectly melted and creamy.", 715, "food273", "Regular", None),
    ("18", "Fatayers", "Juban Fatayer", "Rich and flavorful cheese pastry, popular for its creaminess and smooth, melted filling.", 825, "food274", "Single", None),
    ("19", "Fatayers", "Zaatar Fatayer", "Flatbread pastry topped with a fragrant blend of zaatar spices, baked fresh for a crispy bite.", 605, "food271", "Single", None),
    ("20", "Fatayers", "Chicken Fatayer", "Pastry stuffed with spiced chicken filling, baked to golden perfection for a crispy, flavorful bite.", 825, "food275", "Single", None),
    ("21", "Main Course", "House Special Shawarma", "Our signature chicken shawarma with garlic sauce and pickles in a wrap.", 528, "food276", "Regular", None),
    ("22", "Main Course", "House Special Shawarma", "Rich and flavorful cheese pastry, popular for its creaminess and smooth, melted filling.", 880, "food276", "Large", None),
    ("23", "Main Course", "Farrouj Meshwi", "Grilled whole chicken, marinated in Middle Eastern spices, served with garlic sauce and rice.", 1650, "food277", "Half", None),
    ("24", "Main Course", "Farrouj Meshwi", "Grilled whole chicken, marinated in Middle Eastern spices, served with garlic sauce and rice.", 2860, "food277", "Full", None),
    ("25", "Main Course", "Shish Tawook Wrap", "Marinated grilled chicken served in a wrap with garlic sauce and fresh veggies.", 880, "food278", "Regular", None),
    ("26", "Main Course", "Kafta Kebab Wrap", "Grilled kafta kebabs with hummus, onions, and parsley wrapped in flatbread.", 825, "food279", "Regular", None),
    ("27", "Main Course", "OG Crispy Shawarma", "Chicken shawarma with garlic sauce and crispy bread. Make it a meal (Rs 300)", 950, "food280", "Regular", None),
    ("28", "Main Course", "Flafel Wrap", "Falafel patties wrapped in flatbread with tahini sauce and veggies. Make it a meal (Rs 300)", 385, "food281", "Regular", None),
    ("29", "Main Course", "Chicken Shawarma Platter", "Shawarma chicken served with rice, garlic sauce, and pickles — fresh and flavorful.", 1265, "food273", "Regular", "food282"),
    ("30", "Main Course", "Lahori Shawarma Platter", "Spicy Lahori-style shawarma served with pita bread and chutney.", 990, "food283", "Regular", None),
    ("31", "Main Course", "Shish Tawook Platter", "Grilled marinated chicken skewers, served with rice and garlic sauce.", 1650, "food278", "Regular", None),
    ("32", "Main Course", "Kafta Kebab Platter", "Kafta kebab served with rice, garlic sauce, and grilled vegetables.", 1705, "food279", "Regular", None),
    ("33", "Dessert", "Classic Kunafa", "Crispy golden kunafa with melted cheese, sweet syrup, and crushed pistachios.", 1430, "food284", None, None),
    ("34", "Dessert", "Nutella Kunafa", "Crispy golden kunafa with rich Nutella, sweet syrup, and crushed pistachios.", 1430, "food284", None, None),
    ("35", "Dessert", "Nutella Fatayer", "Soft baked fatayer stuffed with rich Nutella, lightly toasted for a warm and chocolatey delight.", 1045, "food285", None, None),
    ("36", "Dessert", "Juban Fatayer with honey", "Soft baked Juban fatayer filled with creamy cheese and drizzled with pure honey.", 880, "food274", None, None),
    ("37", "Dessert", "Mango ice-cream", "Crispy golden kunafa with melted cheese, sweet syrup, and crushed pistachios.", 305, "food276", None, None),
    ("38", "Dessert", "Belgian Chocolate Ice-cream", "Crispy golden kunafa with melted cheese, sweet syrup, and crushed pistachios.", 305, "food288", None, None),
    ("39", "Dessert", "Vanilla Brownie Ice-cream", "Crispy golden kunafa with melted cheese, sweet syrup, and crushed pistachios.", 305, "food289", None, None),
    ("40", "Others", "Mix Grill Platter", "Half Farouj Meshwi, 2 kafta kebabs, 7 pieces of shish tawook, rice, garlic sauce, pickles, and bread", 3080, "food286", "Regular", None),
    ("41", "Drink", "Regular Water Bottle", "Pure and refreshing regular water bottle, served chilled for your comfort.", 120, "food290", "Regular", None),
    ("42", "Drink", "Large Water Bottle", "Pure and refreshing Large water bottle, served chilled for your comfort.", 200, "food291", "Regular", None),
    ("43", "Drink", "Canned Soft Drinks", "Chilled canned soft drinks, served fresh and fizzy for a refreshing boost.", 150, "food292", "Half", None),
    ("44", "Drink", "Fresh Lime", "Freshly squeezed lime drink, cool and refreshing with a zesty citrus twist.", 200, "food293", "Full", None),
    ("45", "Drink", "Mint Margarita", "Refreshing mint margarita blended with fresh mint and lemon for a cool, zesty taste.", 250, "food294", "Regular", None),
    ("46", "Drink", "Turkish Tea", "Authentic Turkish tea, freshly brewed and served hot with rich aroma and bold flavor.", 250, "food295", "Regular", None),
    ("47", "Drink", "Kadak Chai", "Strong and flavorful Kadak Chai, freshly brewed for a bold and comforting taste.", 250, "food296", "Regular", None),
    ("48", "Drink", "Fresh Seasonal Juices", "Fresh seasonal juices made from ripe fruits, naturally sweet and refreshing.", 450, "food297", "Regular", None),
]

CATEGORIES = [
    {"id": "cat_ss_appetizers", "name": "Appetizers", "description": "Starters, salads, and sides from the Shawarma Stop menu."},
    {"id": "cat_ss_fatayers", "name": "Fatayers", "description": "Baked pastries and wraps."},
    {"id": "cat_ss_main_course", "name": "Main Course", "description": "Shawarma, platters, and mains."},
    {"id": "cat_ss_dessert", "name": "Dessert", "description": "Kunafa, fatayer desserts, and ice cream."},
    {"id": "cat_ss_drink", "name": "Drink", "description": "Beverages."},
    {"id": "cat_ss_others", "name": "Others", "description": "Platters and specials."},
]

CAT_MAP = {
    "Appetizers": "cat_ss_appetizers",
    "Fatayers": "cat_ss_fatayers",
    "Main Course": "cat_ss_main_course",
    "Dessert": "cat_ss_dessert",
    "Drink": "cat_ss_drink",
    "Others": "cat_ss_others",
}


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    products = []
    for row in ROWS:
        fid, cat, name, desc, price, img_key, badge, img2_key = row
        item = {
            "frontendId": fid,
            "categoryKey": cat,
            "categoryId": CAT_MAP[cat],
            "name": name,
            "description": desc,
            "price": float(price),
            "priceLabel": f"Rs {int(price)}",
            "image": FIGMA[img_key],
            "badge": badge,
        }
        if img2_key:
            item["image2"] = FIGMA[img2_key]
        products.append(item)

    payload = {
        "schemaVersion": 1,
        "source": "Shawarma Stop web menu — src/lib/menuItems.ts + menuAssets.ts",
        "categories": CATEGORIES,
        "products": products,
    }
    out_path = out_dir / "shawarma_menu_products.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(products)} products)")


if __name__ == "__main__":
    main()
