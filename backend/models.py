from sqlalchemy import Column, Integer, String
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    price = Column(Integer)
    originalPrice = Column(Integer)
    image = Column(String)
    tags = Column(String) # Comma separated list of tags
    occasions = Column(String) # Comma separated list of occasions
    budgetTier = Column(String)
    season = Column(String)

class CommunityProfile(Base):
    __tablename__ = "community_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    handle = Column(String, index=True)
    avatar = Column(String)
    role = Column(String) # 'creator' or 'user'
    dna_json = Column(String) # JSON string of their DNA percentages
    dna_label = Column(String) # e.g. "Y2K Minimalist"
    recent_purchases = Column(String) # JSON list of product IDs they bought
