import uuid
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    class RoomType(models.TextChoices):
        GROUP = 'group', 'Group'
        PRIVATE = 'private', 'Private'
        SIMULATION = 'simulation', 'Simulation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=15, choices=RoomType.choices, default=RoomType.PRIVATE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'

    def __str__(self):
        return self.name or f"Room({self.id})"


class ChatParticipant(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        TEACHER = 'teacher', 'Teacher'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats', on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, related_name='participants', on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Participant'
        verbose_name_plural = 'Chat Participants'
        unique_together = ('user', 'chat_room')

    def __str__(self):
        return f"{self.user.email} -> {self.chat_room}"


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_sent', on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email}: {self.text[:50]}..."
