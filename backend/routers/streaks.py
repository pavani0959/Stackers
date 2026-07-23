from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from dependencies import get_current_user
from services.streak_service import StreakService
from models import User, StreakSubmission

router = APIRouter(prefix="/api/streaks", tags=["streaks"])

class StreakSubmitRequest(BaseModel):
    image_b64: str

@router.get("/today")
def get_today_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = StreakService(db)
    task = service.get_or_create_today_task()
    
    # Check if user submitted today
    submitted = db.query(StreakSubmission).filter(
        StreakSubmission.user_id == current_user.id,
        StreakSubmission.task_id == task.id,
        StreakSubmission.verification_status == "approved"
    ).first() is not None
    
    return {
        "task_id": task.id,
        "prompt_text": task.prompt_text,
        "date": task.task_date,
        "is_submitted": submitted
    }

@router.post("/submit")
def submit_streak(
    request: StreakSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = StreakService(db)
    try:
        result = service.submit_task(current_user.id, request.image_b64)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Submit error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leaderboard")
def get_leaderboard(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    service = StreakService(db)
    return service.get_leaderboard(limit=limit, offset=offset)

@router.get("/me")
def get_my_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = StreakService(db)
    return service.get_user_streak(current_user.id)
