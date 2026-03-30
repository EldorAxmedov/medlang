from core.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    """Category uchun barcha DB operatsiyalari."""

    def get_by_name(self, name: str):
        return self.get_one(name=name)

    def list_all(self):
        return self.model.objects.all().order_by('name')

    def exists(self, name: str) -> bool:
        return self.model.objects.filter(name=name).exists()


class WordRepository(BaseRepository):
    """Word uchun barcha DB operatsiyalari."""

    def get_by_term(self, term: str):
        return self.get_one(term__iexact=term)

    def get_with_relations(self, term: str):
        """So'zni barcha tarjima, ta'rif va misollari bilan qaytaradi."""
        return (
            self.model.objects
            .prefetch_related('translations', 'definitions', 'examples', 'categories')
            .filter(term__iexact=term)
            .first()
        )

    def get_by_id_with_relations(self, pk):
        return (
            self.model.objects
            .prefetch_related('translations', 'definitions', 'examples', 'categories')
            .filter(pk=pk)
            .first()
        )

    def search(self, query: str, limit: int = 50):
        return (
            self.model.objects
            .filter(term__icontains=query)
            .order_by('term')[:limit]
        )

    def filter_by_category(self, category, limit: int = 100):
        return (
            self.model.objects
            .filter(categories=category)
            .order_by('term')[:limit]
        )

    def filter_by_difficulty(self, level: int):
        return self.model.objects.filter(difficulty=level).order_by('term')

    def list_all(self, limit: int = 200, offset: int = 0):
        return self.model.objects.all().order_by('term')[offset: offset + limit]

    def exists(self, term: str) -> bool:
        return self.model.objects.filter(term__iexact=term).exists()


class TranslationRepository(BaseRepository):
    """Translation uchun barcha DB operatsiyalari."""

    def list_for_word(self, word):
        return self.model.objects.filter(word=word)

    def get_primary(self, word):
        return self.model.objects.filter(word=word, is_primary=True).first()

    def get_by_language(self, word, language: str):
        return self.model.objects.filter(word=word, language=language).first()

    def unset_primary(self, word):
        """Berilgan so'z uchun barcha primary flagni o'chiradi."""
        self.model.objects.filter(word=word, is_primary=True).update(is_primary=False)


class DefinitionRepository(BaseRepository):
    """Definition uchun barcha DB operatsiyalari."""

    def list_for_word(self, word):
        return self.model.objects.filter(word=word)

    def delete_for_word(self, word):
        self.model.objects.filter(word=word).delete()


class ExampleRepository(BaseRepository):
    """Example uchun barcha DB operatsiyalari."""

    def list_for_word(self, word):
        return self.model.objects.filter(word=word)

    def delete_for_word(self, word):
        self.model.objects.filter(word=word).delete()
