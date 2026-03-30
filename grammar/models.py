import uuid
from django.db import models
from django.conf import settings


class GrammarCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='grammar_checks', on_delete=models.CASCADE)
    original_text = models.TextField()
    corrected_text = models.TextField(blank=True)
    # Errors JSON ko'rinishida saqlanadi (offset, length, type, suggestion)
    # Masalan: [{"offset": 5, "length": 4, "type": "spelling", "suggestion": "heart"}]
    error_details = models.JSONField(default=list, blank=True)
    score = models.PositiveSmallIntegerField(default=0) # 0-100
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Grammar Check'
        verbose_name_plural = 'Grammar Checks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Check({self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')})"
