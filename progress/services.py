from django.db import transaction

from progress.models import Level, UserProgress, Certificate
from analytics.services import AnalyticsService
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
        analytics_service: AnalyticsService = None,
    ):
        self.level_repo = level_repo or _level_repo()
        self.progress_repo = progress_repo or _progress_repo()
        self.analytics_service = analytics_service or AnalyticsService()

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
        
        # --- Avtomatik Statistika va Logging ---
        try:
            # 1. Individual Activity Log
            self.analytics_service.log_activity(
                user=user,
                module=activity_type or 'progress',
                action='complete',
                data={'points': points}
            )
            
            # 2. Daily Global Stats (mapping activity_type to daily stat field)
            stat_field_map = {
                'test': 'tests_taken',
                'simulation': 'simulations_started',
                'vocabulary_quiz': 'tests_taken'  # Vocab quiz fits into tests taken generally
            }
            if activity_type in stat_field_map:
                self.analytics_service.increment_daily_stat(stat_field_map[activity_type])
        except Exception:
            # Statistika xatoligi asosiy jarayonni to'xtatmasligi kerak
            pass

        # --- Avtomatik Sertifikat Berish ---
        self._check_and_award_certificates(user, progress.total_score)
        
        return progress

    def _check_and_award_certificates(self, user, total_score):
        """Milestone'lar asosida sertifikat berish."""
        milestones = [
            (500, "Medical English Foundations", "500 ball to'plaganingiz va Medical Resident darajasiga yetganingiz uchun."),
            (2000, "Intermediate Medical Communication", "2000 ball to'plaganingiz va Specialist darajasiga yetganingiz uchun."),
            (5000, "Advanced Clinical Proficiency", "5000 ball to'plaganingiz va Senior Consultant darajasiga yetganingiz uchun."),
            (10000, "Medical English Mastery", "10,000 ball to'plaganingiz va eng yuqori Doctor of Medicine darajasiga yetganingiz uchun.")
        ]
        
        for threshold, title, desc in milestones:
            if total_score >= threshold:
                # Agar ushbu sertifikat hali berilmagan bo'lsa
                if not Certificate.objects.filter(user=user, title=title).exists():
                    Certificate.objects.create(
                        user=user,
                        title=title,
                        description=desc
                    )

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
