import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Word(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=255, db_index=True)
    transcription = models.CharField(max_length=200, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=1)
    categories = models.ManyToManyField(Category, related_name='words', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Word'
        verbose_name_plural = 'Words'
        indexes = [
            models.Index(fields=['term']),
        ]

    def __str__(self):
        return self.term


class Translation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.ForeignKey(Word, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10, default='en')
    text = models.CharField(max_length=1024)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Translation'
        verbose_name_plural = 'Translations'

    def __str__(self):
        return f"{self.word.term} -> {self.text} ({self.language})"


class Definition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.ForeignKey(Word, related_name='definitions', on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        verbose_name = 'Definition'
        verbose_name_plural = 'Definitions'

    def __str__(self):
        return f"Def: {self.word.term}"


class Example(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.ForeignKey(Word, related_name='examples', on_delete=models.CASCADE)
    sentence = models.TextField()
    translation = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Example'
        verbose_name_plural = 'Examples'

    def __str__(self):
        return f"Ex: {self.word.term}"
