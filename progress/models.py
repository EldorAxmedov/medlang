import uuid
import random
import string
from django.db import models
from django.conf import settings


class Level(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    threshold = models.PositiveIntegerField(help_text="Ushbu darajaga yetish uchun kerak bo'lgan ball.")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon name")

    class Meta:
        verbose_name = 'Level'
        verbose_name_plural = 'Levels'
        ordering = ['threshold']

    def __str__(self):
        return f"{self.name} ({self.threshold}+ pts)"


class UserProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='progress', on_delete=models.CASCADE)
    level = models.ForeignKey(Level, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    
    total_score = models.PositiveIntegerField(default=0)
    completed_tests = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    words_learned = models.PositiveIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'

    def __str__(self):
        return f"Progress({self.user.email}): {self.total_score} pts"


def generate_certificate_id():
    """Professional CERT-XXXXXXXX format."""
    chars = string.ascii_uppercase + string.digits
    return 'CERT-' + ''.join(random.choices(chars, k=8))


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='certificates', on_delete=models.CASCADE)
    
    unique_number = models.CharField(
        max_length=20, 
        unique=True, 
        default=generate_certificate_id,
        help_text="Sertifikatning unikal seriya raqami"
    )
    title = models.CharField(max_length=200, help_text="Masalan: Medical English Fundamentals")
    description = models.TextField(blank=True, help_text="Sertifikat nima uchun berilganligi haqida")
    
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Kelajakda PDF va QR kodlarni saqlash uchun
    qr_code = models.ImageField(upload_to='certificates/qrcodes/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='certificates/pdfs/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.unique_number} - {self.user.email}"
