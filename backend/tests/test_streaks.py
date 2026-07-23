import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import User, DailyTask, StreakSubmission, UserStreak
from services.streak_service import StreakService

@pytest.fixture
def db_session(migrated_test_database):
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_daily_task_generation(db_session: Session):
    service = StreakService(db_session)
    # The client is mocked or missing in tests, so it uses fallback
    task1 = service.get_or_create_today_task()
    task2 = service.get_or_create_today_task()
    
    # Should be the exactly same row
    assert task1.id == task2.id
    
    # Check DB constraint
    # Try inserting another task for today directly to verify constraint
    with pytest.raises(IntegrityError):
        new_task = DailyTask(task_date=task1.task_date, prompt_text="Duplicate")
        db_session.add(new_task)
        db_session.commit()
    db_session.rollback()

def test_streak_increment_and_reset(db_session: Session):
    service = StreakService(db_session)
    # mock get_today_date and get_yesterday_date
    original_today = service._get_today_date
    original_yesterday = service._get_yesterday_date
    
    # Setup test user
    user = User(name="Test User", email="teststreak@example.com")
    db_session.add(user)
    db_session.commit()
    
    try:
        # Day 1
        service._get_today_date = lambda: datetime(2024, 1, 1).date()
        service._get_yesterday_date = lambda: datetime(2023, 12, 31).date()
        service.submit_task(user.id, "dummy_b64")
        
        streak = service.get_user_streak(user.id)
        assert streak["current_streak"] == 1
        assert streak["longest_streak"] == 1
        
        # Day 2
        service._get_today_date = lambda: datetime(2024, 1, 2).date()
        service._get_yesterday_date = lambda: datetime(2024, 1, 1).date()
        service.submit_task(user.id, "dummy_b64")
        
        streak = service.get_user_streak(user.id)
        assert streak["current_streak"] == 2
        assert streak["longest_streak"] == 2
        
        # Day 4 (Missed Day 3)
        service._get_today_date = lambda: datetime(2024, 1, 4).date()
        service._get_yesterday_date = lambda: datetime(2024, 1, 3).date()
        service.submit_task(user.id, "dummy_b64")
        
        streak = service.get_user_streak(user.id)
        assert streak["current_streak"] == 1 # Reset!
        assert streak["longest_streak"] == 2 # Best still 2
        
    finally:
        service._get_today_date = original_today
        service._get_yesterday_date = original_yesterday

def test_duplicate_submission_rejected(db_session: Session):
    service = StreakService(db_session)
    user = User(name="Test User 2", email="teststreak2@example.com")
    db_session.add(user)
    db_session.commit()
    
    # First submission passes
    service.submit_task(user.id, "dummy")
    
    # Second submission fails
    with pytest.raises(ValueError, match="Already completed today"):
        service.submit_task(user.id, "dummy")

def test_leaderboard_ordering(db_session: Session):
    service = StreakService(db_session)
    
    user1 = User(name="U1", email="u1@example.com")
    user2 = User(name="U2", email="u2@example.com")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    streak1 = UserStreak(user_id=user1.id, current_streak=5, longest_streak=10, last_completed_date=service._get_today_date())
    streak2 = UserStreak(user_id=user2.id, current_streak=3, longest_streak=15, last_completed_date=service._get_today_date())
    db_session.add_all([streak1, streak2])
    db_session.commit()
    
    lb = [u for u in service.get_leaderboard() if u["user_id"] in (user1.id, user2.id)]
    # U1 has higher current_streak so should be first
    assert lb[0]["user_id"] == user1.id
    assert lb[1]["user_id"] == user2.id
    
    # Now simulate U1 breaking streak
    streak1.last_completed_date = datetime(2020, 1, 1).date()
    db_session.commit()
    
    lb2 = [u for u in service.get_leaderboard() if u["user_id"] in (user1.id, user2.id)]
    # U1 streak should be evaluated as 0, so U2 is first
    assert lb2[0]["user_id"] == user2.id
    assert lb2[1]["user_id"] == user1.id
    assert lb2[1]["current_streak"] == 0
