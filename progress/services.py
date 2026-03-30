from django.db import transaction

from progress.models import Level, UserProgress
from progress.repositories import (
    LevelRepository,
    UserProgressRepository,
)


# ─── Singleton repositories ─────────────────────────────────────

def _level_repo() -> LevelRepository:
    return LevelRepository(Level)


def _progress_repo() -> UserProgressRepository:
    return UserProgressRepository(UserProgress)


# ─── ProgressService ────────────────────────────────────────────

class ProgressService:
    """
    Progress tizimi biznes mantiq.
    Ballarni hisoblash va darajalarni (level) boshqaradi.
    """

    def __init__(
        self,
        level_repo: LevelRepository = None,
        progress_repo: UserProgressRepository = None,
    ):
        self.level_repo = level_repo or _level_repo()
        self.progress_repo = progress_repo or _progress_repo()

    # ── Progressni yangilash ────────────────────────────────────

    @transaction.atomic
    def record_activity(self, user, points: int, activity_type: str = None) -> UserProgress:
        """
        Bajarilgan amal uchun ball berish va progressni yangilash.
        activity_type: 'test', 'simulation', 'vocabulary'
        """
        progress, created = self.progress_repo.model.objects.get_or_create(user=user)
        
        progress.total_score += points
        
        if activity_type == 'test':
            progress.completed_tests += 1
        elif activity_type == 'simulation':
            progress.completed_sessions += 1
        elif activity_type == 'vocabulary':
            progress.words_learned += 1

        # Darajani tekshirish
        new_level = self.level_repo.find_level_for_score(progress.total_score)
        if new_level:
            progress.level = new_level

        progress.save()
        return progress

    # ── Ma'lumotlarni ko'rish ───────────────────────────────────

    def get_user_rank(self, user_id) -> dict:
        progress = self.progress_repo.get_by_user(user_id)
        if not progress:
            return {"score": 0, "level": "Novice"}
            
        return {
            "score": progress.total_score,
            "level": progress.level.name if progress.level else "Novice",
            "stats": {
                "tests": progress.completed_tests,
                "simulations": progress.completed_sessions,
                "words": progress.words_learned
            }
        }

    def get_leaderboard(self, limit: int = 10):
        return self.progress_repo.leaderboard(limit=limit)

    # ── Leveling ─────────────────────────────────────────────

    @transaction.atomic
    def initialize_levels(self):
        """Standard darajalarni yaratish."""
        levels_data = [
            {"name": "Medical Student", "threshold": 0, "icon": "user-graduate"},
            {"name": "Intern", "threshold": 500, "icon": "hospital-user"},
            {"name": "Resident", "threshold": 1500, "icon": "stethoscope"},
            {"name": "Attending Physician", "threshold": 5000, "icon": "user-doctor"},
            {"name": "Medical Professor", "threshold": 12000, "icon": "award"},
        ]
        
        for data in levels_data:
            self.level_repo.model.objects.get_or_create(
                name=data['name'], 
                defaults={"threshold": data['threshold'], "icon": data['icon']}
            )
