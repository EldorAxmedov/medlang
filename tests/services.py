from django.db import transaction
from decimal import Decimal

from tests.models import Test, Question, Answer, UserResult
from tests.repositories import (
    TestRepository,
    QuestionRepository,
    AnswerRepository,
    UserResultRepository,
)


# ─── Singleton repositories (factory) ───────────────────────────

def _test_repo() -> TestRepository:
    return TestRepository(Test)


def _question_repo() -> QuestionRepository:
    return QuestionRepository(Question)


def _answer_repo() -> AnswerRepository:
    return AnswerRepository(Answer)


def _user_result_repo() -> UserResultRepository:
    return UserResultRepository(UserResult)


# ─── TestService ────────────────────────────────────────────────

class TestService:
    """
    Barcha testga bog'liq biznes mantiq.
    """

    def __init__(
        self,
        test_repo: TestRepository = None,
        question_repo: QuestionRepository = None,
        answer_repo: AnswerRepository = None,
        user_result_repo: UserResultRepository = None,
    ):
        self.test_repo = test_repo or _test_repo()
        self.question_repo = question_repo or _question_repo()
        self.answer_repo = answer_repo or _answer_repo()
        self.user_result_repo = user_result_repo or _user_result_repo()

    # ── Yaratish ────────────────────────────────────────────────

    @transaction.atomic
    def create_test(
        self,
        title: str,
        description: str = '',
        category=None,
        difficulty: int = 1,
        questions_data: list[dict] = None,
    ) -> Test:
        """
        questions_data = [{'text': '...', 'answers': [{'text': '...', 'is_correct': True}, ...]}]
        """
        test = self.test_repo.create(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
        )

        if questions_data:
            for q_data in questions_data:
                q = self.question_repo.create(test=test, text=q_data['text'])
                answers = q_data.get('answers', [])
                for a_data in answers:
                    self.answer_repo.create(question=q, **a_data)

        return test

    # ── O'qish ──────────────────────────────────────────────────

    def list_tests(self, category_id=None, limit: int = 100, offset: int = 0):
        if category_id:
            return self.test_repo.filter_by_category(category_id, limit=limit)
        return self.test_repo.list_all(limit=limit, offset=offset)

    def get_test_with_questions(self, pk) -> Test | None:
        """Testni barcha savol va variantlari bilan birga qaytaradi."""
        return self.test_repo.get_with_relations(pk)

    # ── Natijalarni hisoblash ────────────────────────────────────

    @transaction.atomic
    def submit_test(self, user, test_id: str, answers_map: dict[str, str]) -> UserResult:
        """
        answers_map = {'question_id': 'answer_id'}
        """
        test = self.test_repo.get_one(pk=test_id)
        if not test:
            raise ValueError(f"Test topilmadi: '{test_id}'")

        questions = self.question_repo.list_for_test(test_id)
        total_questions = questions.count()
        correct_counter = 0

        # Berilgan javoblarni tekshirish
        for q in questions:
            user_answer_id = answers_map.get(str(q.id))
            if user_answer_id:
                correct_answer = self.answer_repo.get_correct_for_question(q.id)
                if correct_answer and str(correct_answer.id) == user_answer_id:
                    correct_counter += 1

        # Ballni hisoblash (foizda)
        if total_questions > 0:
            score = (Decimal(correct_counter) / Decimal(total_questions)) * Decimal(100)
        else:
            score = Decimal(0)

        # Natijani saqlash
        return self.user_result_repo.create(
            user=user,
            test=test,
            score=score.quantize(Decimal('0.01')),
            total_questions=total_questions,
            correct_answers=correct_counter,
        )

    def get_user_results(self, user_id, limit: int = 50):
        return self.user_result_repo.list_for_user(user_id, limit=limit)
