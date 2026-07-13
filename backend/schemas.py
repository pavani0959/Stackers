from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str
    brand: str
    price: int
    originalPrice: int
    image: str
    tags: list[str]
    occasions: list[str]
    budgetTier: str
    season: str


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class DNARequest(BaseModel):
    tags: list[str]


class PurchaseItem(BaseModel):
    id: int | None = None
    name: str = ""
    price: int | None = None
    image: str = ""
    date: str = ""
    occasion: str = ""
    dnaMatch: int | None = None
    reason: str = ""
    tags: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    name: str = ""
    identityName: str = ""
    dna: dict = Field(default_factory=dict)
    occasions: list[str] = Field(default_factory=list)
    budget: str = "campus-casual"
    purchaseMemory: list[PurchaseItem] = Field(default_factory=list)


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


class ReverseProduct(ProductWithConfidence):
    nlp_score: int
    final_score: int
    category: str


class ReverseOutfit(BaseModel):
    index: int
    title: str
    score: int
    total: int
    within_budget: bool
    items: list[ReverseProduct]


class ReverseShoppingResponse(BaseModel):
    prompt: str
    budget_limit: int
    budget_source: str
    matched_terms: list[str] = Field(default_factory=list)
    within_budget: bool
    message: str
    outfits: list[ReverseOutfit] = Field(default_factory=list)
    closest_total: int | None = None
    closest_over_by: int | None = None
    reused_items: bool = False


class CommunityProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    handle: str
    avatar: str
    role: str
    dna: dict
    dna_label: str
    recent_purchases: list[int]


class BlendRequest(BaseModel):
    user_profile: UserProfile
    creator_dna: dict
    blend_percentage: int


class ChatRequest(BaseModel):
    message: str
    user_profile: UserProfile


class MuseResponse(BaseModel):
    reply: str
    intent: str
    recommendations: list[ProductResponse] = Field(default_factory=list)
