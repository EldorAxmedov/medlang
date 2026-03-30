from core.repositories.base import BaseRepository


class GrammarCheckRepository(BaseRepository):
    """GrammarCheck uchun barcha DB operatsiyalari."""

    def list_for_user(self, user_id, limit: int = 20, offset: int = 0):
        return self.model.objects.filter(user_id=user_id).order_by('-created_at')[offset: offset + limit]

    def get_latest(self, user_id):
        return self.model.objects.filter(user_id=user_id).order_by('-created_at').first()

    def count_by_user(self, user_id):
        return self.model.objects.filter(user_id=user_id).count()

    def clear_for_user(self, user_id):
        self.model.objects.filter(user_id=user_id).delete()
