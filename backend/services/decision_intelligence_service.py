from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

import models
from errors import AppError, NotFoundError
from repositories.recommendation_repository import (
    RecommendationRepository,
)
from services.decision_score_calculator import (
    DECISION_MODEL_VERSION,
    DecisionScoreCalculator,
)
from services.explanation_generator import ExplanationGenerator
from services.regret_signal_service import RegretSignalService


class DecisionIntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = RecommendationRepository(db)
        self.score_calculator = DecisionScoreCalculator()
        self.explanation_generator = ExplanationGenerator()
        self.regret_signal_service = RegretSignalService()

    def create_product_decision(
        self,
        *,
        user_id: int,
        product_id: int,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        user = self.repository.get_user(user_id)
        if user is None:
            raise NotFoundError("User not found")

        product = self.repository.get_product(product_id)
        if product is None:
            raise NotFoundError("Product not found")

        style_profile = self._require_style_profile(user_id)
        preferences = self.repository.get_preferences(user_id)
        wardrobe_items = self.repository.get_active_wardrobe_items(user_id)
        calculation = self.score_calculator.calculate(
            style_profile=style_profile,
            preferences=preferences,
            product=product,
            wardrobe_items=wardrobe_items,
            context=context,
        )
        return_count = self.repository.count_category_returns(
            user_id=user_id,
            category=product.category,
        )
        regret_signals = self.regret_signal_service.generate(
            product=product,
            preferences=preferences,
            score_breakdown=calculation["score_breakdown"],
            category_return_count=return_count,
        )
        explanation = self.explanation_generator.generate(
            product=product,
            overall_score=calculation["overall_score"],
            score_breakdown=calculation["score_breakdown"],
        )
        evidence_sources = self._build_evidence_sources(
            calculation["score_breakdown"],
            category_return_count=return_count,
        )

        try:
            session = self.repository.create_session(
                user_id=user_id,
                style_profile=style_profile,
                context=context,
                model_version=DECISION_MODEL_VERSION,
            )
            item = self.repository.create_item(
                session_id=session.id,
                product=product,
                rank=1,
                overall_score=calculation["overall_score"],
                score_breakdown=calculation["score_breakdown"],
                explanation=explanation,
                evidence_sources=evidence_sources,
                regret_signals=regret_signals,
            )
            self.db.commit()
            self.db.refresh(item)
        except Exception:
            self.db.rollback()
            raise

        return self.serialize_snapshot(item)

    def create_feed(
        self,
        *,
        user_id: int,
        limit: int,
        anti_trend: bool,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        user = self.repository.get_user(user_id)
        if user is None:
            raise NotFoundError("User not found")
        style_profile = self._require_style_profile(user_id)

        preferences = self.repository.get_preferences(user_id)
        wardrobe_items = self.repository.get_active_wardrobe_items(user_id)
        products = self.repository.list_active_products()

        scored: list[dict[str, Any]] = []
        for product in products:
            calculation = self.score_calculator.calculate(
                style_profile=style_profile,
                preferences=preferences,
                product=product,
                wardrobe_items=wardrobe_items,
                context=context,
            )
            return_count = self.repository.count_category_returns(
                user_id=user_id,
                category=product.category,
            )
            regret_signals = self.regret_signal_service.generate(
                product=product,
                preferences=preferences,
                score_breakdown=calculation["score_breakdown"],
                category_return_count=return_count,
            )
            explanation = self.explanation_generator.generate(
                product=product,
                overall_score=calculation["overall_score"],
                score_breakdown=calculation["score_breakdown"],
            )
            scored.append(
                {
                    "product": product,
                    "overall_score": calculation["overall_score"],
                    "score_breakdown": calculation["score_breakdown"],
                    "explanation": explanation,
                    "evidence_sources": self._build_evidence_sources(
                        calculation["score_breakdown"],
                        category_return_count=return_count,
                    ),
                    "regret_signals": regret_signals,
                }
            )

        scored.sort(
            key=lambda result: result["overall_score"],
            reverse=not anti_trend,
        )
        selected = scored[:limit]

        try:
            session = self.repository.create_session(
                user_id=user_id,
                style_profile=style_profile,
                context={
                    **context,
                    "anti_trend": anti_trend,
                    "limit": limit,
                },
                model_version=DECISION_MODEL_VERSION,
            )
            items = []
            for rank, result in enumerate(selected, start=1):
                item = self.repository.create_item(
                    session_id=session.id,
                    product=result["product"],
                    rank=rank,
                    overall_score=result["overall_score"],
                    score_breakdown=result["score_breakdown"],
                    explanation=result["explanation"],
                    evidence_sources=result["evidence_sources"],
                    regret_signals=result["regret_signals"],
                )
                items.append(item)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
        except Exception:
            self.db.rollback()
            raise

        return {
            "session_id": session.id,
            "model_version": session.model_version,
            "profile_version": session.profile_version,
            "items": [self.serialize_snapshot(item) for item in items],
        }

    def get_snapshot(
        self,
        *,
        user_id: int,
        snapshot_id: UUID,
    ) -> dict[str, Any]:
        item = self.repository.get_snapshot(
            user_id=user_id,
            snapshot_id=snapshot_id,
        )
        if item is None:
            raise NotFoundError("Decision snapshot not found")
        return self.serialize_snapshot(item)

    def get_memory(
        self,
        *,
        user_id: int,
    ) -> dict[str, Any]:
        entries = self.repository.list_memory_entries(user_id=user_id)
        return {
            "items": [
                {
                    "event": {
                        "id": event.id,
                        "event_type": event.event_type,
                        "occurred_at": event.occurred_at,
                        "metadata": dict(event.event_metadata or {}),
                    },
                    "decision": self.serialize_snapshot(item),
                }
                for event, item in entries
            ]
        }

    def serialize_snapshot(
        self,
        item: models.RecommendationItem,
    ) -> dict[str, Any]:
        session = item.session
        return {
            "snapshot_id": item.snapshot_id,
            "recommendation_item_id": item.id,
            "session_id": session.id,
            "product": dict(item.product_snapshot or {}),
            "overall_score": int(round(item.overall_score)),
            "score_breakdown": dict(item.score_breakdown or {}),
            "explanation": dict(item.explanation or {}),
            "evidence_sources": dict(item.evidence_sources or {}),
            "regret_signals": list(item.regret_signals or []),
            "model_version": session.model_version,
            "profile_version": session.profile_version,
            "created_at": item.created_at,
        }

    def _require_style_profile(
        self,
        user_id: int,
    ) -> models.StyleProfile:
        style_profile = self.repository.get_latest_style_profile(user_id)
        if style_profile is None:
            raise AppError(
                "Complete your Fashion DNA before requesting recommendations.",
                status_code=status.HTTP_409_CONFLICT,
                code="FASHION_DNA_REQUIRED",
            )
        return style_profile

    @staticmethod
    def _build_evidence_sources(
        score_breakdown: dict[str, dict[str, Any]],
        *,
        category_return_count: int,
    ) -> dict[str, Any]:
        return {
            component_name: {
                "source": component["evidence_source"],
                "evidence": component["evidence"],
            }
            for component_name, component in score_breakdown.items()
        } | {
            "category_return_history": {
                "source": "user_events",
                "return_count": category_return_count,
            }
        }
