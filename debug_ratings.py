#!/usr/bin/env python3

from app.core.database import SessionLocal
from app.models.menu import MenuItem
from app.models.review import Review

def debug_ratings():
    db = SessionLocal()

    try:
        # Get first product
        product = db.query(MenuItem).first()
        reviews = db.query(Review).filter(Review.product_id == product.id).all()

        print(f"Product: {product.name}")
        print(f"Stored rating: {product.rating}")
        print(f"Reviews count: {len(reviews)}")

        # Simulate API logic
        rating = product.rating  # Use stored rating as default
        if reviews:
            rating = sum(r.rating for r in reviews) / len(reviews)

        print(f"Calculated rating: {rating}")
        print(f"Final rating: {round(rating, 1)}")

        # Check a few more products
        print("\nChecking a few more products:")
        products = db.query(MenuItem).limit(3).all()
        for p in products:
            reviews_p = db.query(Review).filter(Review.product_id == p.id).all()
            rating_p = p.rating if not reviews_p else sum(r.rating for r in reviews_p) / len(reviews_p)
            print(f"  {p.name}: stored={p.rating}, reviews={len(reviews_p)}, final={round(rating_p, 1)}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_ratings()
