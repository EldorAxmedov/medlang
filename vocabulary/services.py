from django.db import transaction

from vocabulary.models import Category, Word, Translation, Definition, Example
from vocabulary.repositories import (
    CategoryRepository,
    WordRepository,
    TranslationRepository,
    DefinitionRepository,
    ExampleRepository,
)


# ─── Singleton repositories (DI o'rniga oddiy factory) ────────────────────────

def _category_repo() -> CategoryRepository:
    return CategoryRepository(Category)


def _word_repo() -> WordRepository:
    return WordRepository(Word)


def _translation_repo() -> TranslationRepository:
    return TranslationRepository(Translation)


def _definition_repo() -> DefinitionRepository:
    return DefinitionRepository(Definition)


def _example_repo() -> ExampleRepository:
    return ExampleRepository(Example)


# ─── CategoryService ──────────────────────────────────────────────────────────

class CategoryService:
    def __init__(self, repo: CategoryRepository = None):
        self.repo = repo or _category_repo()

    def get_or_create(self, name: str, description: str = '') -> Category:
        """Mavjud bo'lsa topib qaytaradi, yo'q bo'lsa yangi yaratadi."""
        existing = self.repo.get_by_name(name)
        if existing:
            return existing
        return self.repo.create(name=name, description=description)

    def list_all(self):
        return self.repo.list_all()

    def get_by_name(self, name: str) -> Category | None:
        return self.repo.get_by_name(name)

    def delete(self, name: str) -> bool:
        """Nomi bo'yicha kategoriyani o'chiradi. True — o'chirildi, False — topilmadi."""
        cat = self.repo.get_by_name(name)
        if not cat:
            return False
        self.repo.delete(cat)
        return True


# ─── WordService ──────────────────────────────────────────────────────────────

class WordService:
    """
    Barcha lug'at biznes qoidalari shu sinfda.
    Repository'lar DI orqali yoki default factory orqali qabul qilinadi.
    """

    def __init__(
        self,
        word_repo: WordRepository = None,
        category_repo: CategoryRepository = None,
        translation_repo: TranslationRepository = None,
        definition_repo: DefinitionRepository = None,
        example_repo: ExampleRepository = None,
    ):
        self.word_repo = word_repo or _word_repo()
        self.category_repo = category_repo or _category_repo()
        self.translation_repo = translation_repo or _translation_repo()
        self.definition_repo = definition_repo or _definition_repo()
        self.example_repo = example_repo or _example_repo()

    # ── Yaratish ──────────────────────────────────────────────────────────────

    @transaction.atomic
    def create_word(
        self,
        term: str,
        transcription: str = '',
        difficulty: int = 1,
        categories: list = None,
        translations: list[dict] = None,
        definitions: list[dict] = None,
        examples: list[dict] = None,
    ) -> Word:
        """
        Yangi so'z yaratadi.

        translations = [{'language': 'uz', 'text': 'yurak', 'is_primary': True}]
        definitions  = [{'text': 'The organ that pumps blood.'}]
        examples     = [{'sentence': '...', 'translation': '...'}]
        """
        if self.word_repo.exists(term):
            raise ValueError(f"So'z allaqachon mavjud: '{term}'")

        word = self.word_repo.create(
            term=term,
            transcription=transcription,
            difficulty=difficulty,
        )

        if categories:
            word.categories.set(categories)

        if translations:
            for t in translations:
                self.translation_repo.create(word=word, **t)

        if definitions:
            for d in definitions:
                self.definition_repo.create(word=word, **d)

        if examples:
            for e in examples:
                self.example_repo.create(word=word, **e)

        return word

    # ── O'qish ────────────────────────────────────────────────────────────────

    def get_word(self, term: str) -> Word | None:
        """So'zni topadi (related fields yuklanmagan)."""
        return self.word_repo.get_by_term(term)

    def get_word_with_details(self, term: str) -> Word | None:
        """So'zni barcha tarjima, ta'rif va misollari bilan qaytaradi (bir so'rov)."""
        return self.word_repo.get_with_relations(term)

    def get_word_by_id(self, pk) -> Word | None:
        return self.word_repo.get_by_id_with_relations(pk)

    def list_all(self, limit: int = 200, offset: int = 0):
        return self.word_repo.list_all(limit=limit, offset=offset)

    def search(self, query: str, limit: int = 50):
        if not query or len(query.strip()) < 1:
            raise ValueError("Qidirish so'zi bo'sh bo'lishi mumkin emas.")
        return self.word_repo.search(query.strip(), limit=limit)

    def list_by_category(self, category_name: str, limit: int = 100):
        cat = self.category_repo.get_by_name(category_name)
        if not cat:
            raise ValueError(f"Kategoriya topilmadi: '{category_name}'")
        return self.word_repo.filter_by_category(cat, limit=limit)

    def list_by_difficulty(self, level: int):
        if level < 1 or level > 5:
            raise ValueError("Qiyinchilik darajasi 1–5 oralig'ida bo'lishi kerak.")
        return self.word_repo.filter_by_difficulty(level)

    # ── Yangilash ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def update_word(self, term: str, **fields) -> Word:
        """
        So'zning asosiy maydonlarini yangilaydi.
        Ruxsat etilgan maydonlar: transcription, difficulty.
        """
        word = self.word_repo.get_by_term(term)
        if not word:
            raise ValueError(f"So'z topilmadi: '{term}'")

        allowed = {'transcription', 'difficulty'}
        invalid = set(fields) - allowed
        if invalid:
            raise ValueError(f"Ruxsatsiz maydonlar: {invalid}")

        return self.word_repo.update(word, **fields)

    @transaction.atomic
    def add_translation(self, term: str, language: str, text: str, is_primary: bool = False) -> Translation:
        word = self.word_repo.get_by_term(term)
        if not word:
            raise ValueError(f"So'z topilmadi: '{term}'")

        if is_primary:
            self.translation_repo.unset_primary(word)

        return self.translation_repo.create(
            word=word, language=language, text=text, is_primary=is_primary
        )

    @transaction.atomic
    def add_definition(self, term: str, text: str) -> Definition:
        word = self.word_repo.get_by_term(term)
        if not word:
            raise ValueError(f"So'z topilmadi: '{term}'")
        return self.definition_repo.create(word=word, text=text)

    @transaction.atomic
    def add_example(self, term: str, sentence: str, translation: str = '') -> Example:
        word = self.word_repo.get_by_term(term)
        if not word:
            raise ValueError(f"So'z topilmadi: '{term}'")
        return self.example_repo.create(word=word, sentence=sentence, translation=translation)

    # ── O'chirish ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def delete_word(self, term: str) -> bool:
        """So'zni va unga bog'liq barcha ma'lumotlarni o'chiradi (CASCADE)."""
        word = self.word_repo.get_by_term(term)
        if not word:
            return False
        self.word_repo.delete(word)
        return True
