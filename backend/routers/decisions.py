from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from config import get_settings
from database import get_db
from services.decision_intelligence_service import (
    DecisionIntelligenceService,
)

settings = get_settings()

router = APIRouter(
    prefix="/api/decisions",
    tags=["decision intelligence"],
)


@router.post(
    "/products/{product_id}",
    response_model=schemas.DecisionSnapshotResponse,
    status_code=201,
)
def create_product_decision(
    product_id: int,
    payload: schemas.ProductDecisionRequest,
    db: Session = Depends(get_db),
):
    context = payload.context.model_dump()
    context["source"] = "product_detail"
    return DecisionIntelligenceService(db).create_product_decision(
        user_id=settings.demo_user_id,
        product_id=product_id,
        context=context,
    )


@router.post(
    "/feed",
    response_model=schemas.DecisionFeedResponse,
    status_code=201,
)
def create_decision_feed(
    payload: schemas.DecisionFeedRequest,
    db: Session = Depends(get_db),
):
    context = payload.context.model_dump()
    context["source"] = "feed"
    return DecisionIntelligenceService(db).create_feed(
        user_id=settings.demo_user_id,
        limit=payload.limit,
        anti_trend=payload.anti_trend,
        context=context,
    )


# Keep this route above /{snapshot_id}; otherwise "memory" can be
# interpreted as a UUID path value before this handler is reached.
@router.get(
    "/memory",
    response_model=schemas.DecisionMemoryResponse,
)
def get_decision_memory(
    db: Session = Depends(get_db),
):
    return DecisionIntelligenceService(db).get_memory(
        user_id=settings.demo_user_id,
    )


@router.get(
    "/{snapshot_id}",
    response_model=schemas.DecisionSnapshotResponse,
)
def get_decision_snapshot(
    snapshot_id: UUID,
    db: Session = Depends(get_db),
):
    return DecisionIntelligenceService(db).get_snapshot(
        user_id=settings.demo_user_id,
        snapshot_id=snapshot_id,
    )
