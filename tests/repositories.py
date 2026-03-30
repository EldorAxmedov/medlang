from core.repositories.base import BaseRepository


class TestRepository(BaseRepository):
    """Test uchun barcha DB operatsiyalari."""

    def filter_by_category(self, category_id, limit: int = 100):
        return self.model.objects.filter(category_id=category_id).order_by('-created_at')[:limit]

    def get_with_relations(self, pk):
        """Testni barcha savollari va variantlari bilan qaytaradi (select_related)."""
        return self.model.objects.prefetch_related('questions__answers').filter(pk=pk).first()

    def list_all(self, limit: int = 100, offset: int = 0):
        return self.model.objects.all().order_by('-created_at')[offset: offset + limit]


class QuestionRepository(BaseRepository):
    """Question uchun barcha DB operatsiyalari."""

    def list_for_test(self, test_id):
        return self.model.objects.filter(test_id=test_id).prefetch_related('answers')


class AnswerRepository(BaseRepository):
    """Answer uchun barcha DB operatsiyalari."""
    
    def list_for_question(self, question_id):
        return self.model.objects.filter(question_id=question_id)

    def get_correct_for_question(self, question_id):
        return self.model.objects.filter(question_id=question_id, is_correct=True).first()


class UserResultRepository(BaseRepository):
    """UserResult uchun barcha DB operatsiyalari."""

    def list_for_user(self, user_id, limit: int = 50):
        return self.model.objects.filter(user_id=user_id).order_by('-completed_at')[:limit]

    def get_highest_score(self, user_id, test_id):
        return self.model.objects.filter(user_id=user_id, test_id=test_id).order_by('-score').first()
