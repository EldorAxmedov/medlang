from django.utils import timezone
from core.repositories.base import BaseRepository


class ActivityLogRepository(BaseRepository):
    """ActivityLog uchun barcha DB operatsiyalari."""

    def list_for_user(self, user_id, limit: int = 50):
        return self.model.objects.filter(user_id=user_id).order_by('-timestamp')[:limit]

    def count_activity(self, module=None, action=None, since=None):
        qs = self.model.objects.all()
        if module:
            qs = qs.filter(module=module)
        if action:
            qs = qs.filter(action=action)
        if since:
            qs = qs.filter(timestamp__gte=since)
        return qs.count()


class DailyStatisticRepository(BaseRepository):
    """DailyStatistic uchun barcha DB operatsiyalari."""

    def get_by_date(self, date):
        return self.model.objects.filter(date=date).first()

    def list_recent(self, limit: int = 30):
        return self.model.objects.all().order_by('-date')[:limit]
        
    def get_or_create_today(self):
        today = timezone.now().date()
        return self.model.objects.get_or_create(date=today)
