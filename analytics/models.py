import uuid
from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    class Module(models.TextChoices):
        VOCAB = 'vocabulary', 'Vocabulary'
        TEST = 'test', 'Test'
        GRAMMAR = 'grammar', 'Grammar Check'
        SIMULATION = 'simulation', 'Simulation'
        CHAT = 'chat', 'Chat'

    class Action(models.TextChoices):
        VIEW = 'view', 'View/Open'
        START = 'start', 'Start'
        COMPLETE = 'complete', 'Complete'
        SUBMIT = 'submit', 'Submit'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='activity_logs', on_delete=models.CASCADE)
    module = models.CharField(max_length=20, choices=Module.choices)
    action = models.CharField(max_length=20, choices=Action.choices)
    data = models.JSONField(default=dict, blank=True, help_text="Metadata for the action")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.module}:{self.action} at {self.timestamp}"


class DailyStatistic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    active_users = models.PositiveIntegerField(default=0)
    tests_taken = models.PositiveIntegerField(default=0)
    simulations_started = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Daily Statistic'
        verbose_name_plural = 'Daily Statistics'
        ordering = ['-date']

    def __str__(self):
        return str(self.date)
