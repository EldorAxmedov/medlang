import random
from typing import List, Dict
from .models import Word, Translation

class QuizService:
    """
    Lug'atlardan avtomatik test (quiz) tuzish xizmati.
    """

    def generate_quiz(self, limit: int = 10) -> List[Dict]:
        """
        Tasodifiy lug'at testini generatsiya qiladi.
        """
        # 1. Bazadan yetarli miqdorda so'zlar olish (MCQ uchun)
        words = list(Word.objects.prefetch_related('translations').all())
        if len(words) < 4:
            raise ValueError("Test tuzish uchun lug'atda kamida 4 ta so'z bo'lishi kerak.")

        # Tasodifiy tanlash
        selected_words = random.sample(words, min(limit, len(words)))
        all_translations = list(Translation.objects.all())

        quiz_data = []
        for word in selected_words:
            # To'g'ri tarjima (birinchi primary yoki birinchisini olamiz)
            correct_trans = word.translations.filter(is_primary=True).first() or word.translations.first()
            if not correct_trans:
                continue

            # Noto'g'ri variantlarni tanlash (boshqa so'zlarning tarjimalari)
            # Matni to'g'ri javob bilan bir xil bo'lmagan tarjimalarni olamiz
            wrong_pool = [
                t for t in all_translations 
                if t.word_id != word.id and t.text.strip().lower() != correct_trans.text.strip().lower()
            ]
            
            # Variantlar matni takrorlanmasligi uchun set dan foydalanamiz
            unique_wrong_samples = []
            seen_texts = {correct_trans.text.strip().lower()}
            
            # Tasodifiy tanlab, takrorlanmasligini tekshiramiz
            random.shuffle(wrong_pool)
            for t in wrong_pool:
                text_lower = t.text.strip().lower()
                if text_lower not in seen_texts:
                    unique_wrong_samples.append(t)
                    seen_texts.add(text_lower)
                if len(unique_wrong_samples) >= 3:
                    break
            
            if len(unique_wrong_samples) < 3:
                continue

            # Variantlar ro'yxati
            options = [
                {"id": str(correct_trans.id), "text": correct_trans.text, "is_correct": True},
                {"id": str(unique_wrong_samples[0].id), "text": unique_wrong_samples[0].text, "is_correct": False},
                {"id": str(unique_wrong_samples[1].id), "text": unique_wrong_samples[1].text, "is_correct": False},
                {"id": str(unique_wrong_samples[2].id), "text": unique_wrong_samples[2].text, "is_correct": False},
            ]
            random.shuffle(options)

            quiz_data.append({
                "word_id": str(word.id),
                "question": f"'{word.term}' so'zining tarjimasi qaysi?",
                "options": options
            })

        return quiz_data
