import logging
from datetime import datetime, timezone
import json
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from google import genai

from models import DailyTask, StreakSubmission, UserStreak
from config import get_settings

logger = logging.getLogger(__name__)

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class GeminiTaskResponse(BaseModel):
    task: str

class GeminiVerificationResponse(BaseModel):
    passed: bool
    reasoning: str

class StreakService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        if self.settings.gemini_api_key:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
        else:
            self.client = None

    def _get_today_str(self) -> str:
        return utc_now().strftime("%Y-%m-%d")
        
    def _get_yesterday_str(self) -> str:
        from datetime import timedelta
        return (utc_now() - timedelta(days=1)).strftime("%Y-%m-%d")

    def get_or_create_today_task(self) -> DailyTask:
        today_str = self._get_today_str()
        task = self.db.query(DailyTask).filter(DailyTask.task_date == today_str).first()
        
        if task:
            return task
            
        # Generate new task
        if not self.client:
            prompt_text = "Wear something blue" # fallback
        else:
            system_prompt = """You are a fashion AI. Your job is to generate a single, short, unambiguous, visually-verifiable daily fashion task for a user.
It should be something most people have in their wardrobe. Examples: "wear something yellow", "wear a graphic tee", "wear blue denim".
DO NOT include any conversational text, just return the JSON."""
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Generate today's fashion task.",
                    config={
                        "system_instruction": system_prompt,
                        "response_mime_type": "application/json",
                        "response_schema": GeminiTaskResponse.model_json_schema()
                    }
                )
                result = GeminiTaskResponse.model_validate_json(response.text)
                prompt_text = result.task
            except Exception as e:
                logger.error(f"Failed to generate task: {e}")
                prompt_text = "Wear a watch or accessory" # fallback

        new_task = DailyTask(task_date=today_str, prompt_text=prompt_text)
        self.db.add(new_task)
        try:
            self.db.commit()
            self.db.refresh(new_task)
            return new_task
        except IntegrityError:
            self.db.rollback()
            # Another thread might have created it
            return self.db.query(DailyTask).filter(DailyTask.task_date == today_str).first()

    def submit_task(self, user_id: int, image_b64: str) -> dict:
        today_task = self.get_or_create_today_task()
        today_str = self._get_today_str()
        
        # Check if already submitted today
        existing_submission = self.db.query(StreakSubmission).filter(
            StreakSubmission.user_id == user_id,
            StreakSubmission.task_id == today_task.id,
            StreakSubmission.verification_status == "approved"
        ).first()
        
        if existing_submission:
            raise ValueError("Already completed today's task.")
            
        # Verify with Gemini
        passed = False
        reasoning = "AI Verification unavailable."
        
        if self.client:
            try:
                system_prompt = f"""You are an AI verification judge. The user was asked to complete this fashion task: "{today_task.prompt_text}".
Look at the provided image and determine if they completed the task.
Be reasonably lenient but require actual visual evidence.
Respond with a JSON containing a boolean 'passed' and a string 'reasoning' explaining why."""
                
                # We need to construct the part for the image
                # The image_b64 string probably comes with data:image/jpeg;base64,...
                # genai expects standard base64 if passing directly, or we can use the specific type
                import base64
                if "," in image_b64:
                    mime, data = image_b64.split(",", 1)
                    mime_type = mime.split(":")[1].split(";")[0]
                else:
                    mime_type = "image/jpeg"
                    data = image_b64
                    
                image_bytes = base64.b64decode(data)
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {"mime_type": mime_type, "data": image_bytes},
                        "Did I complete the task?"
                    ],
                    config={
                        "system_instruction": system_prompt,
                        "response_mime_type": "application/json",
                        "response_schema": GeminiVerificationResponse.model_json_schema()
                    }
                )
                result = GeminiVerificationResponse.model_validate_json(response.text)
                passed = result.passed
                reasoning = result.reasoning
            except Exception as e:
                logger.error(f"Verification failed: {e}")
                # Fallback to rejecting if AI fails to parse
                passed = False
                reasoning = "Could not verify image due to an internal error."

        # Save submission
        status = "approved" if passed else "rejected"
        submission = StreakSubmission(
            user_id=user_id,
            task_id=today_task.id,
            image_url="base64_image_data", # we shouldn't store the full base64 in DB realistically, but for this demo we'll just store a stub or something small
            verification_status=status,
            verified_at=utc_now() if passed else None,
            ai_verification_notes=reasoning
        )
        self.db.add(submission)
        
        # Update streak if passed
        if passed:
            user_streak = self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
            if not user_streak:
                user_streak = UserStreak(
                    user_id=user_id,
                    current_streak=1,
                    longest_streak=1,
                    last_completed_date=today_str
                )
                self.db.add(user_streak)
            else:
                yesterday_str = self._get_yesterday_str()
                if user_streak.last_completed_date == yesterday_str:
                    user_streak.current_streak += 1
                elif user_streak.last_completed_date != today_str:
                    user_streak.current_streak = 1
                
                if user_streak.current_streak > user_streak.longest_streak:
                    user_streak.longest_streak = user_streak.current_streak
                    
                user_streak.last_completed_date = today_str

        self.db.commit()
        return {"passed": passed, "reasoning": reasoning}

    def get_leaderboard(self, limit: int = 10, offset: int = 0):
        from sqlalchemy import desc
        from models import User
        
        # We should also handle broken streaks on the leaderboard?
        # A simple approach: we just return current_streak as is.
        # But if the current_streak is broken (last_completed_date < yesterday), it should logically be 0.
        # Let's adjust it dynamically.
        
        streaks = self.db.query(UserStreak, User).join(User, UserStreak.user_id == User.id).order_by(
            desc(UserStreak.current_streak), desc(UserStreak.longest_streak)
        ).offset(offset).limit(limit).all()
        
        today_str = self._get_today_str()
        yesterday_str = self._get_yesterday_str()
        
        results = []
        for streak, user in streaks:
            current = streak.current_streak
            # Dynamically compute broken streaks
            if streak.last_completed_date and streak.last_completed_date != today_str and streak.last_completed_date != yesterday_str:
                current = 0
                
            results.append({
                "user_id": user.id,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "current_streak": current,
                "longest_streak": streak.longest_streak
            })
            
        # Re-sort because we might have changed current_streak
        results.sort(key=lambda x: (x["current_streak"], x["longest_streak"]), reverse=True)
        return results

    def get_user_streak(self, user_id: int):
        streak = self.db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
        today_str = self._get_today_str()
        yesterday_str = self._get_yesterday_str()
        
        if not streak:
            return {"current_streak": 0, "longest_streak": 0, "last_completed_date": None}
            
        current = streak.current_streak
        if streak.last_completed_date and streak.last_completed_date != today_str and streak.last_completed_date != yesterday_str:
            current = 0
            
        return {
            "current_streak": current,
            "longest_streak": streak.longest_streak,
            "last_completed_date": streak.last_completed_date
        }
