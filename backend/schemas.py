from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    name: str
    brand: str
    price: int
    originalPrice: int
    image: str
    tags: List[str]
    occasions: List[str]
    budgetTier: str
    season: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True

class DNARequest(BaseModel):
    tags: List[str]

class PurchaseItem(BaseModel):
    tags: List[str] = []

class UserProfile(BaseModel):
    dna: dict = {}
    occasions: List[str] = []
    budget: str = "campus-casual"
    purchaseMemory: List[PurchaseItem] = []

class ConfidenceScore(BaseModel):
    overall: int
    styleMatch: int
    occasionMatch: int
    budgetMatch: int
    weatherMatch: int
    wardrobeMatch: int

class ProductWithConfidence(ProductResponse):
    confidence: ConfidenceScore

class FeedRequest(BaseModel):
    user_profile: UserProfile
    anti_trend: bool = False

class ReverseShoppingRequest(BaseModel):
    prompt: str
    user_profile: UserProfile

class CommunityProfileResponse(BaseModel):
    id: int
    name: str
    handle: str
    avatar: str
    role: str
    dna: dict
    dna_label: str
    recent_purchases: List[int]
    
    class Config:
        orm_mode = True

class BlendRequest(BaseModel):
    user_profile: UserProfile
    creator_dna: dict
    blend_percentage: int

class ChatRequest(BaseModel):
    message: str
    user_profile: UserProfile
