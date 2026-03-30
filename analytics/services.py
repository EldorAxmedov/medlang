from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from analytics.models import ActivityLog, DailyStatistic
from analytics.repositories import (
    ActivityLogRepository,
    DailyStatisticRepository,
)


# ─── Singleton repositories ─────────────────────────────────────

def _log_repo() -> ActivityLogRepository:
    return ActivityLogRepository(ActivityLog)


def _stats_repo() -> DailyStatisticRepository:
    return DailyStatisticRepository(DailyStatistic)


# ─── AnalyticsService ───────────────────────────────────────────

class AnalyticsService:
    """
    Tizim faoliyatini tahlil qilish va statistikani hisoblash.
    """

    def __init__(
        self,
        log_repo: ActivityLogRepository = None,
        stats_repo: DailyStatisticRepository = None,
    ):
        self.log_repo = log_repo or _log_repo()
        self.stats_repo = stats_repo or _stats_repo()

    # ── Logging ────────────────────────────────────────────────

    def log_activity(self, user, module: str, action: str, data: dict = None) -> ActivityLog:
        """User qadamini logga yozadi."""
        return self.log_repo.create(
            user=user,
            module=module,
            action=action,
            data=data or {}
        )

    # ── Reportlarni hisoblash ───────────────────────────────────

    def get_user_activity_summary(self, user_id):
        """User qaysi modullarda ko'p vaqt o'tkazganini hisoblaydi."""
        return (
            self.log_repo.model.objects
            .filter(user_id=user_id)
            .values('module')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

    @transaction.atomic
    def increment_daily_stat(self, field: str):
        """Daily stats ichidagi sonni bittaga oshiradi."""
        allowed_fields = {'tests_taken', 'simulations_started', 'messages_sent', 'active_users'}
        if field not in allowed_fields:
            raise ValueError(f"Ruxsatsiz field: '{field}'")
            
        instance, created = self.stats_repo.get_or_create_today()
        from django.db.models import F
        self.stats_repo.model.objects.filter(id=instance.id).update(**{field: F(field) + 1})

    def get_dashboard_summary(self, days: int = 7):
        """Oxirgi N kunlik umumiy statistikani qaytaradi."""
        return self.stats_repo.list_recent(limit=days)

    def get_global_activity(self):
        """Barcha modullar bo'yicha umumiy foizlarni chiqarish."""
        return (
            self.log_repo.model.objects
            .values('module')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
