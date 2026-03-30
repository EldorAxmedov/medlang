from core.repositories.base import BaseRepository


class LevelRepository(BaseRepository):
    """Level uchun barcha DB operatsiyalari."""

    def list_all(self):
        return self.model.objects.all().order_by('threshold')

    def find_level_for_score(self, score: int):
        """Berilgan ballga mos eng yuqori darajani topadi."""
        return self.model.objects.filter(threshold__lte=score).order_by('-threshold').first()


class UserProgressRepository(BaseRepository):
    """UserProgress uchun barcha DB operatsiyalari."""

    def get_by_user(self, user_id):
        return self.get_one(user_id=user_id)

    def leaderboard(self, limit: int = 10):
        return self.model.objects.all().order_by('-total_score').select_related('user', 'level')[:limit]

    def increment_score(self, user_id, amount: int):
        """Ballni xavfsiz holda oshirish."""
        from django.db.models import F
        self.model.objects.filter(user_id=user_id).update(total_score=F('total_score') + amount)
