from datetime import datetime
from uuid import UUID
from enum import StrEnum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

class EventType(StrEnum):
    VIEW = "view"
    SAVE = "save"
    WISHLIST = "wishlist"
    CART_ADD = "cart_add"
    CART_REMOVE = "cart_remove"
    PURCHASE = "purchase"
    RETURN = "return"
    KEEP = "keep"
    WEAR = "wear"
    WARDROBE_UPLOAD = "wardrobe_upload"
    RECOMMENDATION_ACCEPT = "recommendation_accept"
    RECOMMENDATION_REJECT = "recommendation_reject"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    gender: str | None
    age: int | None
    avatar_url: str | None
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime


class UserPreferenceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)
    budget_tier: str | None = None

    preferred_colours: list[str] = Field(default_factory=list)
    preferred_brands: list[str] = Field(default_factory=list)
    preferred_occasions: list[str] = Field(default_factory=list)
    preferred_aesthetics: list[str] = Field(default_factory=list)
    fit_preferences: list[str] = Field(default_factory=list)

    comfort_priority: float = Field(default=0.5, ge=0, le=1)
    trend_openness: float = Field(default=0.5, ge=0, le=1)

    fashion_goal: str | None = Field(
        default=None,
        max_length=80,
    )
    comfort_expression_balance: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    occasion_priorities: dict[str, float] | None = None

    @model_validator(mode="after")
    def validate_budget_range(self):
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError(
                "budget_min cannot be greater than budget_max"
            )

        return self


class UserPreferenceResponse(UserPreferenceUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class UserIdentityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    gender: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    age: int | None = Field(
        default=None,
        ge=13,
        le=120,
    )
    avatar_url: str | None = Field(
        default=None,
        max_length=2048,
    )
    onboarding_completed: bool | None = None


class StyleProfileCreate(BaseModel):
    dna_vector: dict[str, float]
    primary_identity: str = Field(min_length=1, max_length=100)
    secondary_identity: str | None = Field(
        default=None,
        max_length=100,
    )
    profile_confidence: float = Field(ge=0, le=100)
    source: str = "quiz"
    model_version: str = "dna-v1"

    @field_validator("dna_vector")
    @classmethod
    def validate_dna_vector(
        cls,
        value: dict[str, float],
    ) -> dict[str, float]:
        if not value:
            raise ValueError("dna_vector cannot be empty")

        if any(score < 0 for score in value.values()):
            raise ValueError(
                "dna_vector values cannot be negative"
            )

        if sum(value.values()) <= 0:
            raise ValueError(
                "dna_vector must contain a positive total"
            )

        return value


class StyleProfileResponse(StyleProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    version: int
    created_at: datetime
    profile_id: UUID
    identity: dict = Field(default_factory=dict)
    confidence_breakdown: dict = Field(
        default_factory=dict,
    )
    evidence: dict = Field(default_factory=dict)


class CurrentProfileResponse(BaseModel):
    user: UserResponse
    preferences: UserPreferenceResponse | None
    style_profile: StyleProfileResponse | None


class ProductStructuredResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str | None
    name: str
    brand: str
    description: str | None
    price: float
    originalPrice: float
    image: str

    category: str | None
    subcategory: str | None
    primary_colour: str | None
    gender_segment: str | None

    tags: list[str]
    occasions: list[str]
    sizes: list[str]

    budgetTier: str
    season: str
    stock_quantity: int
    is_active: bool


class UserEventCreate(BaseModel):
    event_type: EventType
    product_id: int | None = None
    wardrobe_item_id: int | None = None
    recommendation_item_id: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime | None = None


class UserEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_type: str
    product_id: int | None
    wardrobe_item_id: int | None
    recommendation_item_id: int | None
    event_metadata: dict[str, Any]
    occurred_at: datetime
    created_at: datetime


class WardrobeItemCreate(BaseModel):
    product_id: int | None = None
    source: str = "purchase"
    name: str
    category: str
    subcategory: str | None = None
    primary_colour: str | None = None
    size: str | None = None
    image_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    purchase_price: float | None = Field(default=None, ge=0)
    purchase_date: datetime | None = None


class WardrobeItemResponse(WardrobeItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    wear_count: int
    last_worn_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RecommendationSessionCreate(BaseModel):
    session_type: str = "feed"
    raw_prompt: str | None = None
    parsed_intent: dict[str, Any] = Field(default_factory=dict)
    model_version: str = "recommendation-v1"


class RecommendationItemCreate(BaseModel):
    product_id: int
    rank: int = Field(ge=1)
    overall_score: float = Field(ge=0, le=100)
    score_breakdown: dict[str, float] = Field(
        default_factory=dict
    )
    explanation: dict[str, Any] = Field(default_factory=dict)
    warning: dict[str, Any] = Field(default_factory=dict)


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

class DNAQuizAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(
        min_length=1,
        max_length=80,
    )
    choice_id: str = Field(
        min_length=1,
        max_length=80,
    )


class DNAProfileCalculateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: list[DNAQuizAnswer]

    @field_validator("answers")
    @classmethod
    def validate_answers(
        cls,
        answers: list[DNAQuizAnswer],
    ) -> list[DNAQuizAnswer]:
        if len(answers) != 8:
            raise ValueError(
                "Exactly eight quiz answers are required."
            )

        question_ids = {
            answer.question_id
            for answer in answers
        }

        if len(question_ids) != 8:
            raise ValueError(
                "Every quiz question must be answered once."
            )

        return answers


class DNAIdentityResponse(BaseModel):
    name: str
    description: str
    primary: str
    secondary: str | None = None


class DNAConfidenceBreakdown(BaseModel):
    quiz_completeness: int
    answer_consistency: int
    preference_coverage: int
    behavior_evidence: int


class DNAEvidenceResponse(BaseModel):
    quiz_answers: int
    behavior_events: int


class DNAProfileResponse(BaseModel):
    profile_id: UUID
    version: int
    dna: dict[str, float]
    identity: DNAIdentityResponse
    confidence: int
    confidence_breakdown: DNAConfidenceBreakdown
    evidence: DNAEvidenceResponse

class CurrentProfileUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    avatar_url: str | None = None
    onboarding_completed: bool = False
    created_at: datetime | None = None


class CurrentProfilePreferenceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    budget_min: int | None = None
    budget_max: int | None = None
    budget_tier: str | None = None

    preferred_occasions: list[str] = Field(
        default_factory=list,
    )
    preferred_colours: list[str] = Field(
        default_factory=list,
    )
    preferred_brands: list[str] = Field(
        default_factory=list,
    )
    preferred_aesthetics: list[str] = Field(
        default_factory=list,
    )
    fit_preferences: list[str] = Field(
        default_factory=list,
    )

    comfort_priority: float = 0.5
    trend_openness: float = 0.5

    fashion_goal: str | None = None

    comfort_expression_balance: float = 0.5

    occasion_priorities: dict[str, float] = Field(
        default_factory=dict,
    )


class CurrentStyleProfileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    profile_id: UUID
    version: int

    dna_vector: dict[str, float] = Field(
        default_factory=dict,
    )

    primary_identity: str
    secondary_identity: str | None = None

    profile_confidence: int

    identity: dict = Field(
        default_factory=dict,
    )

    confidence_breakdown: dict[str, int] = Field(
        default_factory=dict,
    )

    evidence: dict[str, int] = Field(
        default_factory=dict,
    )


class CurrentProfileResponse(BaseModel):
    user: CurrentProfileUserResponse

    preferences: (
        CurrentProfilePreferenceResponse | None
    ) = None

    style_profile: (
        CurrentStyleProfileResponse | None
    ) = None
