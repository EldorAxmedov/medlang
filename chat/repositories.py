from django.db.models import Prefetch
from core.repositories.base import BaseRepository


class ChatRoomRepository(BaseRepository):
    """ChatRoom uchun barcha DB operatsiyalari."""

    def get_with_messages(self, pk, limit: int = 50):
        return self.model.objects.prefetch_related(
            Prefetch('messages', queryset=self.model.objects.model.messages.all().order_by('-created_at')[:limit])
        ).filter(pk=pk).first()

    def list_rooms_for_user(self, user_id):
        return self.model.objects.filter(participants__user_id=user_id).order_by('-created_at')


class ChatParticipantRepository(BaseRepository):
    """ChatParticipant uchun barcha DB operatsiyalari."""

    def list_for_room(self, room_id):
        return self.model.objects.filter(chat_room_id=room_id).select_related('user')

    def find_private_room(self, user1_id, user2_id):
        """Ikki foydalanuvchi orasidagi private roomni qidiradi."""
        # Murakkab mantiq: Har ikkala user qatnashgan 2 kishilik private room
        from chat.models import ChatRoom
        return ChatRoom.objects.filter(
            type=ChatRoom.RoomType.PRIVATE,
            participants__user_id=user1_id
        ).filter(
            participants__user_id=user2_id
        ).first()


class ChatMessageRepository(BaseRepository):
    """ChatMessage uchun barcha DB operatsiyalari."""

    def list_for_room(self, room_id, limit: int = 50, offset: int = 0):
        return self.model.objects.filter(chat_room_id=room_id).order_by('-created_at')[offset: offset + limit]

    def mark_as_read(self, room_id, user_id):
        """User uchun xabarlarni o'qilgan deb belgilaydi (agar sender bo'lmasa)."""
        return self.model.objects.filter(
            chat_room_id=room_id,
            is_read=False
        ).exclude(sender_id=user_id).update(is_read=True)
