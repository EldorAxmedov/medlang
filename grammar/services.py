from grammar.models import GrammarCheck
from grammar.repositories import GrammarCheckRepository


# ─── Singleton repositories ─────────────────────────────────────

def _grammar_check_repo() -> GrammarCheckRepository:
    return GrammarCheckRepository(GrammarCheck)


# ─── GrammarService ─────────────────────────────────────────────

class GrammarService:
    """
    Grammatika va imlo tekshirish biznes mantiq.
    Hozircha model va repository bilan ishlaydi.
    Kelajakda tashqi API (masalan, OpenAI, Grammarly) integratsiyasi shuyerda bo'ladi.
    """

    def __init__(self, repo: GrammarCheckRepository = None):
        self.repo = repo or _grammar_check_repo()
        from .ai_services import GeminiGrammarService
        self.ai_service = GeminiGrammarService()

    # ── Asosiy mantiq ───────────────────────────────────────────

    def process_check(self, user, original_text: str) -> GrammarCheck:
        """
        Matnni AI orqali tekshirish va yutuqlarni yangilash.
        """
        if not original_text or len(original_text.strip()) < 5:
            raise ValueError("Matn juda qisqa.")

        # 1. Gemini orqali tahlil
        analysis_result = self.ai_service.analyze_text(original_text)
        
        # 2. Natijani bazada saqlash
        check = self.repo.create(
            user=user,
            original_text=original_text,
            corrected_text=analysis_result.get("corrected_text", ""),
            error_details=analysis_result.get("errors", []),
            score=max(0, min(100, analysis_result.get("score", 0)))
        )

        # 3. Progressni yangilash (ProgressService integratsiyasi)
        try:
            from progress.services import ProgressService
            # Har bir tekshiruv uchun bazaviy 20 ball + olingan bahoning yarmi
            # (Misol: 80 ball olsa, jami 20 + 40 = 60 activity points)
            points_to_add = 20 + int(check.score / 2)
            ProgressService().record_activity(
                user=user, 
                points=points_to_add, 
                activity_type='grammar'
            )
        except Exception:
            pass

        return check

    def update_result(self, check_id, corrected_text: str, errors: list, score: int) -> GrammarCheck:
        """
        AI servisi tekshirib bo'lgandan so'ng natijani yangilash.
        """
        check = self.repo.get_one(pk=check_id)
        if not check:
            raise ValueError(f"Check topilmadi: '{check_id}'")

        return self.repo.update(
            check,
            corrected_text=corrected_text,
            error_details=errors,
            score=max(0, min(100, score))
        )

    def get_history(self, user_id, limit: int = 10, offset: int = 0):
        return self.repo.list_for_user(user_id, limit=limit, offset=offset)

    def get_user_stats(self, user_id):
        return {
            "total_checks": self.repo.count_by_user(user_id),
            "latest": self.repo.get_latest(user_id)
        }
