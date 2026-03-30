import uuid
from django.db import models
from django.conf import settings


class Test(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    # Re-using vocabulary categories for convenience or can be independent
    category = models.ForeignKey('vocabulary.Category', related_name='tests', on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=1) # 1–5 level
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    class Type(models.TextChoices):
        MCQ = 'mcq', 'Multiple Choice'
        MATCHING = 'matching', 'Terminology Matching'
        GAP_FILL = 'gap_fill', 'Text Completion (Gap Fill)'
        TRUE_FALSE = 'true_false', 'True / False'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=20, choices=Type.choices, default=Type.MCQ)
    text = models.TextField(help_text="Savol matni yoki kontekst matni (gap fill uchun).")
    image = models.ImageField(upload_to='tests/questions/', null=True, blank=True)
    
    # Language Learning specific
    rationale = models.TextField(blank=True, help_text="To'g'ri javob uchun qisqacha izoh (English).")
    hint = models.CharField(max_length=255, blank=True, help_text="Yordamchi ma'lumot (Hint).")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['created_at']

    def __str__(self):
        return f"Q({self.test.title}): {self.text[:50]}..."


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    def __str__(self):
        return f"A({self.question.id}): {self.text[:50]}..."


class UserResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='test_results', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='user_results', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2) # 0.00 to 100.00
    total_questions = models.PositiveSmallIntegerField()
    correct_answers = models.PositiveSmallIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Result'
        verbose_name_plural = 'User Results'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.email} - {self.test.title}: {self.score}%"
