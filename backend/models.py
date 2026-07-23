from __future__ import annotations

from uuid import uuid4
from sqlalchemy import Column, Integer, String, Uuid
from database import Base



from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    seed_key = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )
    name = Column(
        String(120),
        nullable=False,
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    gender = Column(
        String(30),
        nullable=True,
    )
    age = Column(
        Integer,
        nullable=True,
    )
    avatar_url = Column(
        Text,
        nullable=True,
    )
    onboarding_completed = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_synthetic = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    password_hash = Column(
        String(255),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    preferences = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    style_profiles = relationship(
        "StyleProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="StyleProfile.version",
    )
    wardrobe_items = relationship(
        "WardrobeItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    events = relationship(
        "UserEvent",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recommendation_sessions = relationship(
        "RecommendationSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    budget_min = Column(
        Integer,
        nullable=True,
    )
    budget_max = Column(
        Integer,
        nullable=True,
    )
    budget_tier = Column(
        String(50),
        nullable=True,
    )

    preferred_colours = Column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_brands = Column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_occasions = Column(
        JSON,
        nullable=False,
        default=list,
    )
    preferred_aesthetics = Column(
        JSON,
        nullable=False,
        default=list,
    )
    fit_preferences = Column(
        JSON,
        nullable=False,
        default=list,
    )

    comfort_priority = Column(
        Float,
        nullable=False,
        default=0.5,
    )
    trend_openness = Column(
        Float,
        nullable=False,
        default=0.5,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user = relationship(
        "User",
        back_populates="preferences",
    )

    fashion_goal = Column(
        String(80),
        nullable=True,
    )

    comfort_expression_balance = Column(
        Float,
        nullable=False,
        default=0.5,
    )

    occasion_priorities = Column(
        JSON,
        nullable=False,
        default=dict,
    )


class StyleProfile(Base):
    __tablename__ = "style_profiles"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "version",
            name="uq_style_profile_user_version",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(
        Integer,
        nullable=False,
    )

    dna_vector = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    primary_identity = Column(
        String(100),
        nullable=False,
    )
    secondary_identity = Column(
        String(100),
        nullable=True,
    )
    profile_confidence = Column(
        Float,
        nullable=False,
        default=0,
    )

    source = Column(
        String(50),
        nullable=False,
        default="quiz",
    )
    model_version = Column(
        String(50),
        nullable=False,
        default="dna-v1",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user = relationship(
        "User",
        back_populates="style_profiles",
    )

    profile_id = Column(
        Uuid(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    identity = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    confidence_breakdown = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    evidence = Column(
        JSON,
        nullable=False,
        default=dict,
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    sku = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )
    brand = Column(
        String,
        nullable=False,
    )
    description = Column(
        Text,
        nullable=True,
    )

    price = Column(
        Float,
        nullable=False,
    )
    originalPrice = Column(
        Float,
        nullable=False,
    )

    image = Column(
        Text,
        nullable=False,
    )

    category = Column(
        String(50),
        nullable=False,
        index=True,
    )
    subcategory = Column(
        String(80),
        nullable=False,
        index=True,
    )
    primary_colour = Column(
        String(40),
        nullable=False,
        index=True,
    )
    gender_segment = Column(
        String(30),
        nullable=False,
        index=True,
    )

    tags = Column(
        JSON,
        nullable=False,
        default=list,
    )
    occasions = Column(
        JSON,
        nullable=False,
        default=list,
    )
    sizes = Column(
        JSON,
        nullable=False,
        default=list,
    )

    budgetTier = Column(
        String,
        nullable=False,
    )
    season = Column(
        String,
        nullable=False,
    )

    stock_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    wardrobe_items = relationship(
        "WardrobeItem",
        back_populates="product",
    )
    events = relationship(
        "UserEvent",
        back_populates="product",
    )
    recommendation_items = relationship(
        "RecommendationItem",
        back_populates="product",
    )


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(
        Integer,
        primary_key=True,
    )
    seed_key = Column(
        String(120),
        unique=True,
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source = Column(
        String(40),
        nullable=False,
        default="purchase",
    )
    name = Column(
        String(160),
        nullable=False,
    )
    category = Column(
        String(50),
        nullable=False,
    )
    subcategory = Column(
        String(80),
        nullable=True,
    )
    primary_colour = Column(
        String(40),
        nullable=True,
    )
    size = Column(
        String(30),
        nullable=True,
    )
    image_url = Column(
        Text,
        nullable=True,
    )
    tags = Column(
        JSON,
        nullable=False,
        default=list,
    )

    purchase_price = Column(
        Float,
        nullable=True,
    )
    purchase_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    wear_count = Column(
        Integer,
        nullable=False,
        default=0,
    )
    last_worn_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user = relationship(
        "User",
        back_populates="wardrobe_items",
    )
    product = relationship(
        "Product",
        back_populates="wardrobe_items",
    )


class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"

    id = Column(
        Integer,
        primary_key=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    style_profile_id = Column(
        Integer,
        ForeignKey("style_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile_version = Column(
        Integer,
        nullable=False,
    )

    profile_snapshot = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    context_snapshot = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    session_type = Column(
        String(50),
        nullable=False,
        default="feed",
    )
    raw_prompt = Column(
        Text,
        nullable=True,
    )
    parsed_intent = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    model_version = Column(
        String(50),
        nullable=False,
        default="recommendation-v1",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user = relationship(
        "User",
        back_populates="recommendation_sessions",
    )
    items = relationship(
        "RecommendationItem",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="RecommendationItem.rank",
    )


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "rank",
            name="uq_recommendation_session_rank",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
    )
    session_id = Column(
        Integer,
        ForeignKey(
            "recommendation_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    snapshot_id = Column(
        Uuid(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    product_snapshot = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    evidence_sources = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    regret_signals = Column(
        JSON,
        nullable=False,
        default=list,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rank = Column(
        Integer,
        nullable=False,
    )
    overall_score = Column(
        Float,
        nullable=False,
    )
    score_breakdown = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    explanation = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    warning = Column(
        JSON,
        nullable=False,
        default=dict,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    session = relationship(
        "RecommendationSession",
        back_populates="items",
    )
    product = relationship(
        "Product",
        back_populates="recommendation_items",
    )
    events = relationship(
        "UserEvent",
        back_populates="recommendation_item",
    )


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(
        Integer,
        primary_key=True,
    )
    seed_key = Column(
        String(150),
        unique=True,
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    wardrobe_item_id = Column(
        Integer,
        ForeignKey("wardrobe_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    recommendation_item_id = Column(
        Integer,
        ForeignKey(
            "recommendation_items.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    event_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # "metadata" is reserved by SQLAlchemy Declarative, so the Python
    # attribute uses event_metadata while the database column remains metadata.
    event_metadata = Column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )

    occurred_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user = relationship(
        "User",
        back_populates="events",
    )
    product = relationship(
        "Product",
        back_populates="events",
    )
    recommendation_item = relationship(
        "RecommendationItem",
        back_populates="events",
    )


# Keep your current CommunityProfile model here.
class CommunityProfile(Base):
    __tablename__ = "community_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    handle = Column(
        String,
        nullable=False,
    )
    avatar = Column(
        String,
        nullable=False,
    )
    role = Column(
        String,
        nullable=False,
    )
    dna_json = Column(
        Text,
        nullable=False,
    )
    dna_label = Column(
        String,
        nullable=False,
    )
    recent_purchases = Column(
        Text,
        nullable=False,
    )
from sqlalchemy import Date

class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True)
    task_date = Column(Date, unique=True, nullable=False, index=True)
    prompt_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class StreakSubmission(Base):
    __tablename__ = "streak_submissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("daily_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    verification_status = Column(String(20), nullable=False, default="pending")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    ai_verification_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    user = relationship("User", backref="streak_submissions")
    task = relationship("DailyTask", backref="submissions")


class UserStreak(Base):
    __tablename__ = "user_streaks"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_completed_date = Column(Date, nullable=True)

    user = relationship("User", backref="streak")
