import uuid
from django.db import models
from django.conf import settings


class Scenario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    specialty = models.ForeignKey('users.Specialty', related_name='scenarios', on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=1) # 1–5 level
    # Prompt for AI model
    system_prompt = models.TextField(help_text="AI ga beriladigan instruktsiyalar.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Scenario'
        verbose_name_plural = 'Scenarios'

    def __str__(self):
        return self.title


class PatientProfile(models.Model):
    """Ssenariy doirasidagi bemor detali."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.OneToOneField(Scenario, related_name='patient', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    complaint = models.TextField(help_text="Asosiy shikoyat")
    history = models.TextField(help_text="Bemor tarixi (Anamnesis)")

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"{self.name} ({self.age}y/o {self.gender})"


class Session(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='simulations', on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, related_name='sessions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    score = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Simulation Session'
        verbose_name_plural = 'Simulation Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Session({self.user.email} - {self.scenario.title})"


class SimulationMessage(models.Model):
    class Sender(models.TextChoices):
        USER = 'user', 'Doctor/Student'
        PATIENT = 'patient', 'Patient/AI'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=Sender.choices)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Simulation Message'
        verbose_name_plural = 'Simulation Messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}..."
