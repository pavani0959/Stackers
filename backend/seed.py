import os
import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Product, CommunityProfile

# Re-create all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# The real product data
INITIAL_PRODUCTS = [
  { "id": 1, "name": "Clean Fit Oversized Tee", "brand": "H&M", "price": 799, "originalPrice": 1499, "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,neutral,casual,everyday", "occasions": "campus,cafe,dates", "budgetTier": "campus-casual", "season": "all" },
  { "id": 2, "name": "Minimal Cargo Pants", "brand": "Zara", "price": 2490, "originalPrice": 3990, "image": "https://images.unsplash.com/photo-1624378439575-d1ead6bb17f1?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,streetwear,casual,neutral", "occasions": "campus,fest,cafe", "budgetTier": "campus-casual", "season": "all" },
  { "id": 3, "name": "Classic Slim Jeans", "brand": "Levi's", "price": 1899, "originalPrice": 2999, "image": "https://images.unsplash.com/photo-1542272604-780c8d52a5ce?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,classic,neutral,everyday", "occasions": "campus,work,dates,cafe", "budgetTier": "campus-casual", "season": "all" },
  { "id": 4, "name": "Neutral Hoodie", "brand": "Roadster", "price": 999, "originalPrice": 1799, "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=800&auto=format&fit=crop", "tags": "streetwear,casual,neutral,comfort", "occasions": "campus,home,gym", "budgetTier": "smart-spender", "season": "winter" },
  { "id": 5, "name": "White Platform Sneakers", "brand": "HRX", "price": 1299, "originalPrice": 2499, "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,clean,everyday,neutral", "occasions": "campus,dates,cafe,fest", "budgetTier": "campus-casual", "season": "all" },
  { "id": 6, "name": "Linen Button-Up Shirt", "brand": "Marks & Spencer", "price": 1099, "originalPrice": 1999, "image": "https://images.unsplash.com/photo-1596755094514-f87e32f85e2c?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,smart,neutral,classic", "occasions": "work,dates,cafe", "budgetTier": "campus-casual", "season": "summer" },
  { "id": 7, "name": "Sand Tote Bag", "brand": "Aldo", "price": 699, "originalPrice": 1299, "image": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,neutral,everyday,accessory", "occasions": "campus,cafe,dates,travel", "budgetTier": "smart-spender", "season": "all" },
  { "id": 8, "name": "Minimal Watch — Silver", "brand": "Fastrack", "price": 2199, "originalPrice": 3500, "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,clean,classic,accessory", "occasions": "work,dates,campus", "budgetTier": "campus-casual", "season": "all" },
  { "id": 9, "name": "Beige Structured Blazer", "brand": "Arrow", "price": 3499, "originalPrice": 5999, "image": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?q=80&w=800&auto=format&fit=crop", "tags": "quietLuxury,smart,neutral,formal", "occasions": "work,dates,fest", "budgetTier": "style-investor", "season": "all" },
  { "id": 10, "name": "Y2K Graphic Tee", "brand": "H&M", "price": 599, "originalPrice": 999, "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=800&auto=format&fit=crop", "tags": "y2k,bold,streetwear,colorful", "occasions": "fest,concerts,night-out", "budgetTier": "smart-spender", "season": "summer" },
  { "id": 11, "name": "Wide-Leg Trousers", "brand": "Zara", "price": 2299, "originalPrice": 3499, "image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=800&auto=format&fit=crop", "tags": "minimalist,quietLuxury,neutral,smart", "occasions": "work,dates,cafe", "budgetTier": "campus-casual", "season": "all" },
  { "id": 12, "name": "Dark Academia Sweater", "brand": "FabIndia", "price": 1799, "originalPrice": 2899, "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=800&auto=format&fit=crop", "tags": "darkAcademia,classic,cozy,neutral", "occasions": "campus,cafe,concerts", "budgetTier": "campus-casual", "season": "winter" },
  { "id": 13, "name": "Statement Earrings", "brand": "Accessorize", "price": 349, "originalPrice": 699, "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=800&auto=format&fit=crop", "tags": "bold,colorful,accessory,y2k", "occasions": "fest,night-out,dates", "budgetTier": "budget-explorer", "season": "all" },
  { "id": 14, "name": "Running Shoes — Black", "brand": "Nike", "price": 4999, "originalPrice": 7999, "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800&auto=format&fit=crop", "tags": "sporty,clean,everyday,athletic", "occasions": "gym,campus", "budgetTier": "style-investor", "season": "all" },
  { "id": 15, "name": "Denim Jacket — Vintage", "brand": "Levi's", "price": 2999, "originalPrice": 4999, "image": "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?q=80&w=800&auto=format&fit=crop", "tags": "streetwear,classic,casual,cool", "occasions": "campus,fest,cafe,concerts", "budgetTier": "campus-casual", "season": "winter" },
  { "id": 16, "name": "Silk Satin Top — Ivory", "brand": "AND", "price": 1599, "originalPrice": 2499, "image": "https://images.unsplash.com/photo-1564584217132-2271feaeb3c5?q=80&w=800&auto=format&fit=crop", "tags": "quietLuxury,elegant,neutral,feminine", "occasions": "dates,work,night-out", "budgetTier": "campus-casual", "season": "all" },
  { "id": 17, "name": "Cargo Shorts", "brand": "Roadster", "price": 799, "originalPrice": 1299, "image": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?q=80&w=800&auto=format&fit=crop", "tags": "streetwear,casual,comfort,bold", "occasions": "campus,gym,home", "budgetTier": "smart-spender", "season": "summer" },
  { "id": 18, "name": "Chunky Sneakers — White", "brand": "New Balance", "price": 5999, "originalPrice": 8999, "image": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?q=80&w=800&auto=format&fit=crop", "tags": "y2k,streetwear,bold,statement", "occasions": "fest,campus,cafe", "budgetTier": "style-investor", "season": "all" },
  { "id": 19, "name": "Ethnic Printed Kurta", "brand": "Biba", "price": 1299, "originalPrice": 1999, "image": "https://images.unsplash.com/photo-1583391733958-d698142330e3?q=80&w=800&auto=format&fit=crop", "tags": "ethnic,festive,colorful,traditional", "occasions": "puja,festivals,family", "budgetTier": "campus-casual", "season": "all" },
  { "id": 20, "name": "Sports Bralette", "brand": "Puma", "price": 899, "originalPrice": 1499, "image": "https://images.unsplash.com/photo-1622619405698-8424a1b02534?q=80&w=800&auto=format&fit=crop", "tags": "sporty,athletic,comfort,casual", "occasions": "gym,home,campus", "budgetTier": "smart-spender", "season": "summer" }
]

INITIAL_COMMUNITY = [
    {
        "name": "Zendaya",
        "handle": "@zendayastyle",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=200&auto=format&fit=crop",
        "role": "creator",
        "dna_json": json.dumps({"quietLuxury": 60, "bold": 30, "minimalist": 10}),
        "dna_label": "Quiet Luxury Explorer",
        "recent_purchases": json.dumps([9, 16, 7])
    },
    {
        "name": "Ahaan Panday",
        "handle": "@ahaanp",
        "avatar": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=200&auto=format&fit=crop",
        "role": "creator",
        "dna_json": json.dumps({"streetwear": 70, "y2k": 20, "bold": 10}),
        "dna_label": "Streetwear Icon",
        "recent_purchases": json.dumps([2, 4, 18, 15])
    },
    {
        "name": "Tanya G",
        "handle": "@tanyastyles",
        "avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=200&auto=format&fit=crop",
        "role": "creator",
        "dna_json": json.dumps({"minimalist": 80, "campusCasual": 20}),
        "dna_label": "Campus Minimalist",
        "recent_purchases": json.dumps([1, 3, 5])
    },
    {
        "name": "Rahul M",
        "handle": "@rahul_m",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200&auto=format&fit=crop",
        "role": "user",
        "dna_json": json.dumps({"minimalist": 40, "darkAcademia": 40, "vintage": 20}),
        "dna_label": "Dark Scholar",
        "recent_purchases": json.dumps([12, 11, 8])
    }
]

def seed_db():
    db: Session = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            print("Seeding database...")
            for p_data in INITIAL_PRODUCTS:
                product = Product(**p_data)
                db.add(product)
                
            for c_data in INITIAL_COMMUNITY:
                profile = CommunityProfile(**c_data)
                db.add(profile)
                
            db.commit()
            print("Database seeded successfully with products and community!")
        else:
            print("Database already contains data.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
