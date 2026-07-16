from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

import models


PURCHASE_MEMORY_EVENT_TYPES = ("purchase", "keep", "return")


def product_to_snapshot(product: models.Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "price": float(product.price),
        "originalPrice": float(product.originalPrice),
        "image": product.image,
        "category": product.category,
        "subcategory": product.subcategory,
        "primary_colour": product.primary_colour,
        "tags": list(product.tags or []),
        "occasions": list(product.occasions or []),
        "budgetTier": product.budgetTier,
        "season": product.season,
    }


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> models.User | None:
        return self.db.get(models.User, user_id)

    def get_latest_style_profile(
        self,
        user_id: int,
    ) -> models.StyleProfile | None:
        return (
            self.db.query(models.StyleProfile)
            .filter(models.StyleProfile.user_id == user_id)
            .order_by(
                models.StyleProfile.version.desc(),
                models.StyleProfile.id.desc(),
            )
            .first()
        )

    def get_preferences(
        self,
        user_id: int,
    ) -> models.UserPreference | None:
        return (
            self.db.query(models.UserPreference)
            .filter(models.UserPreference.user_id == user_id)
            .first()
        )

    def get_product(
        self,
        product_id: int,
    ) -> models.Product | None:
        return (
            self.db.query(models.Product)
            .filter(
                models.Product.id == product_id,
                models.Product.is_active.is_(True),
            )
            .first()
        )

    def list_active_products(self) -> list[models.Product]:
        return (
            self.db.query(models.Product)
            .filter(models.Product.is_active.is_(True))
            .all()
        )

    def get_active_wardrobe_items(
        self,
        user_id: int,
    ) -> list[models.WardrobeItem]:
        return (
            self.db.query(models.WardrobeItem)
            .filter(
                models.WardrobeItem.user_id == user_id,
                models.WardrobeItem.is_active.is_(True),
            )
            .all()
        )

    def count_category_returns(
        self,
        *,
        user_id: int,
        category: str,
    ) -> int:
        return (
            self.db.query(models.UserEvent)
            .join(
                models.Product,
                models.UserEvent.product_id == models.Product.id,
            )
            .filter(
                models.UserEvent.user_id == user_id,
                models.UserEvent.event_type == "return",
                models.Product.category == category,
            )
            .count()
        )

    def create_session(
        self,
        *,
        user_id: int,
        style_profile: models.StyleProfile,
        context: dict[str, Any],
        model_version: str,
    ) -> models.RecommendationSession:
        session = models.RecommendationSession(
            user_id=user_id,
            style_profile_id=style_profile.id,
            profile_version=style_profile.version,
            session_type=str(context.get("source") or "product_detail"),
            raw_prompt=None,
            parsed_intent=dict(context),
            profile_snapshot={
                "profile_id": str(style_profile.profile_id),
                "version": style_profile.version,
                "dna": dict(style_profile.dna_vector or {}),
                "identity": dict(style_profile.identity or {}),
                "confidence": float(style_profile.profile_confidence),
            },
            context_snapshot=dict(context),
            model_version=model_version,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def create_item(
        self,
        *,
        session_id: int,
        product: models.Product,
        rank: int,
        overall_score: int,
        score_breakdown: dict[str, Any],
        explanation: dict[str, Any],
        evidence_sources: dict[str, Any],
        regret_signals: list[dict[str, Any]],
    ) -> models.RecommendationItem:
        item = models.RecommendationItem(
            session_id=session_id,
            product_id=product.id,
            rank=rank,
            overall_score=overall_score,
            score_breakdown=score_breakdown,
            explanation=explanation,
            warning={},
            product_snapshot=product_to_snapshot(product),
            evidence_sources=evidence_sources,
            regret_signals=regret_signals,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_snapshot(
        self,
        *,
        user_id: int,
        snapshot_id: UUID,
    ) -> models.RecommendationItem | None:
        return (
            self.db.query(models.RecommendationItem)
            .join(models.RecommendationSession)
            .filter(
                models.RecommendationItem.snapshot_id == snapshot_id,
                models.RecommendationSession.user_id == user_id,
            )
            .first()
        )

    def list_memory_entries(
        self,
        *,
        user_id: int,
    ) -> list[tuple[models.UserEvent, models.RecommendationItem]]:
        return (
            self.db.query(
                models.UserEvent,
                models.RecommendationItem,
            )
            .join(
                models.RecommendationItem,
                models.UserEvent.recommendation_item_id
                == models.RecommendationItem.id,
            )
            .join(
                models.RecommendationSession,
                models.RecommendationItem.session_id
                == models.RecommendationSession.id,
            )
            .filter(
                models.UserEvent.user_id == user_id,
                models.RecommendationSession.user_id == user_id,
                models.UserEvent.event_type.in_(
                    PURCHASE_MEMORY_EVENT_TYPES,
                ),
            )
            .order_by(models.UserEvent.occurred_at.desc())
            .all()
        )
