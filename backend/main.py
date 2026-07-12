from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db
import models
import schemas
import json
from ml import calculate_dna_ml, calc_confidence_ml, generate_outfit_nlp, blend_dna, find_twins

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Myntra Identity API")

# Configure CORS so React app can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Myntra Identity API"}

@app.get("/api/products", response_model=List[schemas.ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    # Convert comma separated strings back to lists for the frontend
    for p in products:
        p.tags = p.tags.split(',') if p.tags else []
        p.occasions = p.occasions.split(',') if p.occasions else []
    return products

@app.post("/api/dna/calculate")
def calculate_dna(request: schemas.DNARequest):
    """
    Takes a list of tags from the user's quiz answers and runs
    the ML clustering model to determine their Fashion DNA.
    """
    return calculate_dna_ml(request.tags)

@app.post("/api/recommend/feed", response_model=List[schemas.ProductWithConfidence])
def get_personalized_feed(request: schemas.FeedRequest, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    user_prof = request.user_profile.dict()
    
    feed = []
    for p in products:
        p_dict = {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": p.price,
            "originalPrice": p.originalPrice,
            "image": p.image,
            "tags": p.tags.split(',') if p.tags else [],
            "occasions": p.occasions.split(',') if p.occasions else [],
            "budgetTier": p.budgetTier,
            "season": p.season
        }
        
        confidence = calc_confidence_ml(p_dict, user_prof)
        p_dict["confidence"] = confidence
        feed.append(p_dict)
        
    # Sort by overall confidence descending (or ascending if anti_trend is on)
    feed.sort(key=lambda x: x["confidence"]["overall"], reverse=not request.anti_trend)
    return feed

@app.post("/api/recommend/confidence/{product_id}", response_model=schemas.ConfidenceScore)
def get_product_confidence(product_id: int, request: schemas.FeedRequest, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        return {"error": "Product not found"}
        
    p_dict = {
        "tags": p.tags.split(',') if p.tags else [],
        "occasions": p.occasions.split(',') if p.occasions else [],
        "budgetTier": p.budgetTier,
        "season": p.season
    }
    
    return calc_confidence_ml(p_dict, request.user_profile.dict())

@app.post("/api/recommend/reverse")
def reverse_shopping(request: schemas.ReverseShoppingRequest, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    user_prof = request.user_profile.dict()
    
    all_p = []
    for p in products:
        all_p.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": p.price,
            "originalPrice": p.originalPrice,
            "image": p.image,
            "tags": p.tags.split(',') if p.tags else [],
            "occasions": p.occasions.split(',') if p.occasions else [],
            "budgetTier": p.budgetTier,
            "season": p.season
        })
        
    outfit = generate_outfit_nlp(request.prompt, user_prof, all_p)
    return outfit

@app.post("/api/community/twins")
def get_twins(request: schemas.FeedRequest, db: Session = Depends(get_db)):
    user_dna = request.user_profile.dna
    profiles = db.query(models.CommunityProfile).all()
    
    scored_twins = find_twins(user_dna, profiles)
    
    res = []
    for st in scored_twins:
        prof = st["profile"]
        res.append({
            "id": prof.id,
            "name": prof.name,
            "handle": prof.handle,
            "avatar": prof.avatar,
            "role": prof.role,
            "dna": json.loads(prof.dna_json),
            "dna_label": prof.dna_label,
            "recent_purchases": json.loads(prof.recent_purchases),
            "match_percentage": st["match"]
        })
        
    return res

@app.post("/api/dna/blend")
def blend_user_dna(request: schemas.BlendRequest):
    merged = blend_dna(request.user_profile.dna, request.creator_dna, request.blend_percentage)
    return {"merged_dna": merged}

@app.post("/api/muse/chat")
def muse_chat(request: schemas.ChatRequest):
    from ml import muse_chat_response
    response_text = muse_chat_response(request.message, request.user_profile.dict())
    return {"reply": response_text}

